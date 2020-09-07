import click

from valohai_cli.api import request
from valohai_cli.commands.pipeline.run.utils import build_edges, build_nodes, match_pipeline
from valohai_cli.ctx import get_project
from valohai_cli.messages import success, error


@click.command(
    context_settings=dict(ignore_unknown_options=True),
    add_help_option=False
)
@click.argument('name', required=False, metavar='PIPELINE-NAME')
@click.option('--commit', '-c', default=None, metavar='SHA', help='The commit to use. Defaults to the current HEAD.')
@click.option('--title', '-c', default=None, help='The optional title of the pipeline run.')
@click.pass_context
def run(ctx, name, commit, title):
    """
    Start a pipeline run.
    """
    # Having to explicitly compare to `--help` is slightly weird, but it's because of the nested command thing.
    if name == '--help' or not name:
        click.echo(ctx.get_help(), color=ctx.color)
        try:
            config = get_project(require=True).get_config(commit_identifier=commit)
            if config.pipelines:
                click.secho('\nThese pipelines are available in the selected commit:\n', color=ctx.color, bold=True)
                for pipeline in sorted(config.pipelines):
                    click.echo('   * %s' % pipeline, color=ctx.color)
        except:  # If we fail to extract the pipeline list, it's not that big of a deal.
            pass
        ctx.exit()

    project = get_project(require=True)
    commit = commit or project.resolve_commit()['identifier']
    config = project.get_config()

    matched_pipeline = match_pipeline(config, name)
    pipeline = config.pipelines[matched_pipeline]

    start_pipeline(config, pipeline, project.id, commit, title)


def start_pipeline(config, pipeline, project_id, commit, title=None):
    edges = build_edges(pipeline)
    nodes = build_nodes(commit, config, pipeline)
    payload = {
        "edges": edges,
        "nodes": nodes,
        "project": project_id,
        "title": title or pipeline.name,
    }

    resp = request(
        method='post',
        url='/api/v0/pipelines/',
        json=payload,
    ).json()

    success('Pipeline ={} queued. See {}'.format(resp.get("counter"), resp.get("urls").get("display")))
