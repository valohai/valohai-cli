import contextlib
from typing import Any, Dict, List, Optional, Union

import click
from click import Context
from valohai_yaml.objs import Config, Pipeline
from valohai_yaml.pipelines.conversion import PipelineConverter

from valohai_cli.api import request
from valohai_cli.commands.pipeline.run.utils import match_pipeline
from valohai_cli.ctx import get_project
from valohai_cli.messages import success
from valohai_cli.utils.commits import create_or_resolve_commit


@click.command(
    context_settings={"ignore_unknown_options": True},
    add_help_option=False
)
@click.argument('name', required=False, metavar='PIPELINE-NAME')
@click.option('--commit', '-c', default=None, metavar='SHA', help='The commit to use. Defaults to the current HEAD.')
@click.option('--title', '-c', default=None, help='The optional title of the pipeline run.')
@click.option('--adhoc', '-a', is_flag=True, help='Upload the current state of the working directory, then run it as an ad-hoc execution.')
@click.option('--disable_git_packaging', '-g', is_flag=True, default=False, help='When using ad-hoc execution, whether to disable git for packaging directory contents.')
@click.option('--yaml', default=None, help='The path to the configuration YAML file (valohai.yaml) file to use.')
@click.option('--tag', 'tags', multiple=True, help='Tag the pipeline. May be repeated.')
@click.argument('args', nargs=-1, type=click.UNPROCESSED, metavar='PIPELINE-OPTIONS...')
@click.pass_context
def run(
    ctx: Context,
    name: Optional[str],
    commit: Optional[str],
    title: Optional[str],
    adhoc: bool,
    disable_git_packaging: bool,
    yaml: Optional[str],
    tags: List[str],
    args: List[str],
) -> None:
    """
    Start a pipeline run.
    """
    # Having to explicitly compare to `--help` is slightly weird, but it's because of the nested command thing.
    if name == '--help' or not name:
        click.echo(ctx.get_help(), color=ctx.color)
        print_pipeline_list(ctx, commit)
        ctx.exit()
        return

    project = get_project(require=True)
    assert project

    if yaml and not adhoc:
        raise click.UsageError('--yaml is only valid with --adhoc')

    commit = create_or_resolve_commit(project, commit=commit, adhoc=adhoc, yaml_path=yaml, allow_git_packaging=not disable_git_packaging)
    config = project.get_config(commit_identifier=commit if project.is_remote else None, yaml_path=yaml)

    matched_pipeline = match_pipeline(config, name)
    pipeline = config.pipelines[matched_pipeline]

    start_pipeline(config, pipeline, project.id, commit, tags, args, title)


def process_args(args: List[str]) -> Dict[str, Union[str, list]]:
    args_dict: Dict[str, Union[str, list]] = {}
    for i, arg in enumerate(args):
        if arg.startswith("--"):
            arg_name = arg.lstrip("-")
            if "+=" in arg_name:  # --param+=value
                name, value = arg_name.split("+=", 1)
                value_list: Union[list, str] = args_dict.get(name) or []
                if not isinstance(value_list, list):
                    raise click.UsageError(f'[{name}] Cannot mix "+=" with other parameter assignments')
                value_list.append(value)
                args_dict[name] = value_list
            elif "=" in arg_name:  # --param=value
                name, value = arg_name.split("=", 1)
                if name in args_dict:
                    raise click.UsageError(f'[{name}] Parameter assigned more than once')
                args_dict[name] = value
            else:  # --param value
                if arg_name in args_dict:
                    raise click.UsageError(f'[{arg_name}] Parameter assigned more than once')
                next_arg_idx = i + 1
                if next_arg_idx < len(args) and not args[next_arg_idx].startswith("--"):
                    args_dict[arg_name] = args[next_arg_idx]
                else:  # --param --param2 --param3 (flag)
                    args_dict[arg_name] = "true"  # doesn't support bool as we are using strings for pipeline parameters
    return args_dict


def print_pipeline_list(ctx: Context, commit: Optional[str]) -> None:
    with contextlib.suppress(Exception):  # If we fail to extract the pipeline list, it's not that big of a deal.
        project = get_project(require=True)
        assert project
        config = project.get_config(commit_identifier=commit)
        if config.pipelines:
            click.secho('\nThese pipelines are available in the selected commit:\n', color=ctx.color, bold=True)
            for pipeline_name in sorted(config.pipelines):
                click.echo(f'   * {pipeline_name}', color=ctx.color)


def start_pipeline(
    config: Config,
    pipeline: Pipeline,
    project_id: str,
    commit: str,
    tags: List[str],
    args: List[str],
    title: Optional[str] = None,
) -> None:
    args_dict: Dict[str, Union[str, list]]
    args_dict = process_args(args) if args else {}

    converter = PipelineConverter(config=config, commit_identifier=commit, parameter_arguments=args_dict)
    converted_pipeline = converter.convert_pipeline(pipeline)

    unused_args = [k for k in args_dict if k not in converted_pipeline['parameters']]
    if unused_args:
        if not converted_pipeline['parameters']:
            raise click.UsageError(f'Pipeline does not have any parameters, but parameters were given: {unused_args}')
        raise click.UsageError(f'Unknown pipeline parameters: {unused_args}')

    payload: Dict[str, Any] = {
        "project": project_id,
        "title": title or pipeline.name,
        "tags": tags,
        **converted_pipeline,
    }
    resp = request(
        method='post',
        url='/api/v0/pipelines/',
        json=payload,
    ).json()

    success(f"Pipeline ={resp.get('counter')} queued. See {resp.get('urls').get('display')}")
