import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import success, warn, progress, info
from valohai_cli.range import IntegerRange
from valohai_cli.utils.cli_utils import HelpfulArgument


@click.argument(
    'counters',
    help='Range of execution counters, or "latest"',
    required=False,
    nargs=-1,
    cls=HelpfulArgument,
)
@click.option('--all', default=None, is_flag=True, help='Stop all in-progress executions.')
@click.command()
def stop(counters, all=False):
    """
    Stop one or more in-progress executions.
    """
    project = get_project(require=True)

    if counters == 'all':  # pragma: no cover
        # Makes sense to support this spelling too.
        counters = None
        all = True

    if counters and all:
        # If we spell out latest and ranges in the error message, it becomes kinda
        # unwieldy, so let's just do this.
        raise click.UsageError('Pass execution counter(s), or `--all`, not both.')

    executions = get_executions_for_stop(project, counters, all)

    for execution in executions:
        progress('Stopping #{counter}... '.format(counter=execution['counter']))
        resp = request('post', execution['urls']['stop'])
        info(resp.text)
    success('Done.')


def get_executions_for_stop(project, counters, all):
    params = {'project': project.id}
    if counters == 'latest':
        return [project.get_execution_from_counter('latest')]

    if counters:
        params['counter'] = sorted(IntegerRange.parse(counters).as_set())
    elif all:
        params['status'] = 'incomplete'
    else:
        warn('Nothing to stop (pass #s or `--all`)')
        return []

    return request('get', '/api/v0/executions/', params=params).json()['results']
