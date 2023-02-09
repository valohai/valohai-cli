from datetime import timedelta

import click

from valohai_cli.api import request
from valohai_cli.consts import execution_statuses
from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table


@click.command()
@click.option(
    '--status',
    multiple=True,
    help='Filter by status (default: all)',
    type=click.Choice(sorted(execution_statuses | {'incomplete'}))
)
@click.option(
    '--count',
    '--limit',
    '-n',
    type=int,
    default=9001,
    help='How many executions to show',
)
@click.option('--deleted', '-d', is_flag=True, help='Show only deleted executions')
@click.option('--owned', '-o', is_flag=True, help='Show only executions that I\'ve created')
def list(status: str, count: int, deleted: bool, owned:bool) -> None:
    """
    Show a list of executions for the project.
    """
    project = get_project(require=True)
    assert project
    params = {
        'project': project.id,
        'limit': count,
        'ordering': '-counter',
        'deleted': 'false',
    }
    if status:
        params['status'] = set(status)
    if deleted:
        params['deleted'] = deleted
    if owned:
        params['creator'] = settings.user['id']
    executions = request('get', '/api/v0/executions/', params=params).json()['results']
    if settings.output_format == 'json':
        return print_json(executions)
    if not executions:
        info(f'{project}: No executions.')
        return
    for execution in executions:
        execution['url'] = execution['urls']['display']
        execution['duration'] = str(
            timedelta(seconds=round(execution['duration']))
            if execution['duration']
            else ''
        ).rjust(10)

    print_table(
        executions,
        columns=['counter', 'status', 'step', 'duration', 'url'],
        headers=['#', 'Status', 'Step', 'Duration', 'URL'],
    )
