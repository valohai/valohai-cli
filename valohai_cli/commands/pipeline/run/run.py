import contextlib
from typing import Any, Dict, List, Optional

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
@click.option('--yaml', default=None, help='The path to the configuration YAML file (valohai.yaml) file to use.')
@click.option('--tag', 'tags', multiple=True, help='Tag the pipeline. May be repeated.')
@click.pass_context
def run(
    ctx: Context,
    name: Optional[str],
    commit: Optional[str],
    title: Optional[str],
    adhoc: bool,
    yaml: Optional[str],
    tags: List[str],
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

    commit = create_or_resolve_commit(project, commit=commit, adhoc=adhoc, yaml_path=yaml)
    config = project.get_config()

    matched_pipeline = match_pipeline(config, name)
    pipeline = config.pipelines[matched_pipeline]

    start_pipeline(config, pipeline, project.id, commit, tags, title)


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
    title: Optional[str] = None,
) -> None:
    payload: Dict[str, Any] = {
        "project": project_id,
        "title": title or pipeline.name,
        "tags": tags,
        **PipelineConverter(config=config, commit_identifier=commit).convert_pipeline(pipeline),
    }

    resp = request(
        method='post',
        url='/api/v0/pipelines/',
        json=payload,
    ).json()

    success(f"Pipeline ={resp.get('counter')} queued. See {resp.get('urls').get('display')}")
