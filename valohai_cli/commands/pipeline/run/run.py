from __future__ import annotations

import contextlib
import dataclasses
from typing import Any

import click
from click import Context
from valohai_yaml.objs import Config, ExecutionNode, Pipeline, TaskNode
from valohai_yaml.pipelines.conversion import ConvertedPipeline, PipelineConverter
from valohai_yaml.utils import listify

from valohai_cli.api import request
from valohai_cli.commands.pipeline.run.utils import match_pipeline
from valohai_cli.ctx import get_project
from valohai_cli.messages import success
from valohai_cli.utils.commits import create_or_resolve_commit

run_epilog = (
    "More detailed help (e.g. how to define parameters and inputs) is available when you have "
    "defined which pipeline to run. For instance, if you have a pipeline called Science, "
    'try running "vh exec run Science --help". (This is denoted by PIPELINE-OPTIONS... in the usage.)'
)


@click.command(
    context_settings={"ignore_unknown_options": True},
    add_help_option=False,
    epilog=run_epilog,
)
@click.argument(
    "name",
    required=False,
    metavar="PIPELINE-NAME",
)
@click.option(
    "--commit",
    "-c",
    default=None,
    metavar="SHA",
    help="The commit to use. Defaults to the current HEAD.",
)
@click.option(
    "--title",
    "-t",
    default=None,
    help="The optional title of the pipeline run.",
)
@click.option(
    "--adhoc",
    "-a",
    is_flag=True,
    help="Upload the current state of the working directory, then run it as an ad-hoc execution.",
)
@click.option(
    "--git-packaging/--no-git-packaging",
    "-g/-G",
    default=True,
    is_flag=True,
    help="When creating ad-hoc pipelines, whether to allow using Git for packaging directory contents.",
)
@click.option(
    "--yaml",
    default=None,
    help="The path to the configuration YAML file (valohai.yaml) file to use.",
)
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Tag the pipeline. May be repeated.",
)
@click.option(
    "--environment",
    "-e",
    default=None,
    help='Override environment UUID or slug',
)
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
    metavar="PIPELINE-OPTIONS...",
)
@click.pass_context
def run(
    ctx: Context,
    *,
    name: str | None,
    commit: str | None,
    title: str | None,
    adhoc: bool,
    git_packaging: bool = True,
    yaml: str | None,
    tags: list[str],
    environment: str | None,
    args: list[str],
) -> None:
    """
    Start a pipeline run.
    """
    # Having to explicitly compare to `--help` is slightly weird, but it's because of the nested command thing.
    if name == "--help" or not name:
        click.echo(ctx.get_help(), color=ctx.color)
        print_pipeline_list(ctx, commit)
        ctx.exit()
        return

    project = get_project(require=True)
    assert project

    if yaml and not adhoc:
        raise click.UsageError("--yaml is only valid with --adhoc")

    commit = create_or_resolve_commit(
        project,
        commit=commit,
        adhoc=adhoc,
        yaml_path=yaml,
        allow_git_packaging=git_packaging,
    )
    config = project.get_config(commit_identifier=commit if project.is_remote else None, yaml_path=yaml)

    matched_pipeline = match_pipeline(config, name)
    pipeline = config.pipelines[matched_pipeline]

    start_pipeline(
        config=config,
        pipeline=pipeline,
        project_id=project.id,
        commit=commit,
        tags=tags,
        title=title,
        args=args,
        override_environment=environment,
    )


@dataclasses.dataclass
class ProcessedPipelineArguments:
    pipeline_parameters: dict[str, str | list] = dataclasses.field(default_factory=dict)
    node_parameters: dict[tuple[str, str], str | list] = dataclasses.field(default_factory=dict)


def process_args(args: list[str]) -> ProcessedPipelineArguments:  # noqa: C901
    ppa = ProcessedPipelineArguments()
    actions = []
    for i, arg in enumerate(args):
        if not arg.startswith("--"):
            continue
        arg = arg.removeprefix("--")
        if "+=" in arg:  # --param+=value
            name, _, value = arg.partition("+=")
            node, _, name = name.rpartition(".")
            actions.append((node, name, "append", value))
        elif "=" in arg:  # --param=value
            name, _, value = arg.partition("=")
            node, _, name = name.rpartition(".")
            actions.append((node, name, "set", value))
        else:  # --param value
            node, _, name = arg.rpartition(".")
            next_arg_idx = i + 1
            if next_arg_idx < len(args) and not args[next_arg_idx].startswith("--"):
                value = args[next_arg_idx]
            else:  # --param --param2 --param3 (flag)
                value = "true"  # Stringly typed
            actions.append((node, name, "set", value))

    for node, name, action, value in actions:
        if node:  # Node parameter (or input)
            key = (node, name)
            target = ppa.node_parameters
            display_name = f"{node}.{name}"
        else:
            key = name  # type: ignore[assignment]
            target = ppa.pipeline_parameters  # type: ignore[assignment]
            display_name = name

        if action == "set":
            if key in target:
                raise click.UsageError(f"[{display_name}] Parameter assigned more than once")
            target[key] = value
        elif action == "append":
            value_list: list | str = target.get(key) or []
            if not isinstance(value_list, list):
                raise click.UsageError(f'[{display_name}] Cannot mix "+=" with other parameter assignments')
            value_list.append(value)
            target[key] = value_list
        else:  # pragma: no cover
            raise ValueError("Should never happen...")

    return ppa


def assign_node_parameters(
    *,
    node_parameters: dict[tuple[str, str], str | list],
    config: Config,
    converted_pipeline: ConvertedPipeline,
    pipeline_definition: Pipeline,
) -> None:
    node_definitions = pipeline_definition.node_map
    converted_pipeline_node_map = {node["name"]: node for node in converted_pipeline["nodes"]}
    for (node_name, param_name), value in node_parameters.items():
        if (conv_node := converted_pipeline_node_map.get(node_name)) is None:
            raise click.UsageError(
                f"Node '{node_name}' not found in the pipeline (available nodes: {sorted(converted_pipeline_node_map)})",
            )
        if conv_node["name"] != node_name:
            continue
        node_defn = node_definitions[node_name]
        if not isinstance(node_defn, (ExecutionNode, TaskNode)):
            raise click.UsageError(f"Cannot set parameters for {node_defn.type} node '{node_name}'.")
        step = config.get_step_by(name=node_defn.step)
        if not step:
            raise ValueError(f"Step '{node_defn.step}' referenced by node '{node_name}' not defined.")
        display_name = f"{node_name}.{param_name}"
        if param_name in step.parameters:
            params = conv_node["template"].setdefault("parameters", {})
            params[param_name] = value
        elif param_name in step.inputs:
            not_urls = [v for v in listify(value) if "://" not in str(v)]
            if not_urls:
                raise click.UsageError(f"{display_name}: must be valid URI(s) (invalid: {not_urls}).")
            inputs = conv_node["template"].setdefault("inputs", {})
            inputs[param_name] = value
        else:
            raise click.UsageError(
                f"{display_name} does not refer to a parameter or input in step {step.name} (used by node {node_name}).\n"
                f"Available parameters: {sorted(step.parameters)}.\n"
                f"Available inputs: {sorted(step.inputs)}.",
            )


def print_pipeline_list(ctx: Context, commit: str | None) -> None:
    with contextlib.suppress(
        Exception,
    ):  # If we fail to extract the pipeline list, it's not that big of a deal.
        project = get_project(require=True)
        assert project
        config = project.get_config(commit_identifier=commit)
        if config.pipelines:
            click.secho(
                "\nThese pipelines are available in the selected commit:\n",
                color=ctx.color,
                bold=True,
            )
            for pipeline_name in sorted(config.pipelines):
                click.echo(f"   * {pipeline_name}", color=ctx.color)


def start_pipeline(
    *,
    config: Config,
    pipeline: Pipeline,
    project_id: str,
    commit: str,
    tags: list[str],
    args: list[str],
    title: str | None = None,
    override_environment: str | None = None,
) -> None:
    if "--help" in args:
        raise click.UsageError("Sorry, --help is not presently supported when a pipeline name is specified.")
    ppa = process_args(args)

    converter = PipelineConverter(
        config=config,
        commit_identifier=commit,
        parameter_arguments=ppa.pipeline_parameters,
    )
    converted_pipeline = converter.convert_pipeline(pipeline)

    if override_environment:
        for node in converted_pipeline["nodes"]:
            if node.get("type") in ("execution", "task"):
                node["template"]["environment"] = override_environment

    if ppa.node_parameters:
        assign_node_parameters(
            node_parameters=ppa.node_parameters,
            config=config,
            converted_pipeline=converted_pipeline,
            pipeline_definition=pipeline,
        )

    unused_args = [k for k in ppa.pipeline_parameters if k not in converted_pipeline["parameters"]]
    if unused_args:
        if not converted_pipeline["parameters"]:
            raise click.UsageError(
                f"Pipeline does not have any parameters, but parameters were given: {unused_args}",
            )
        raise click.UsageError(f"Unknown pipeline parameters: {unused_args}")

    payload: dict[str, Any] = {
        "project": project_id,
        "title": title or pipeline.name,
        "tags": tags,
        **converted_pipeline,
    }
    resp = request(
        method="post",
        url="/api/v0/pipelines/",
        json=payload,
    ).json()

    success(f"Pipeline ={resp.get('counter')} queued. See {resp.get('urls').get('display')}")
