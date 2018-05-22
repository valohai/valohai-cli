from operator import itemgetter

import click

from valohai_cli.api import request
from valohai_cli.table import print_table


@click.command()
def list():
    """
    List all projects.
    """
    projects_data = request('get', '/api/v0/projects/', params={'limit': 9000}).json()['results']
    projects_data.sort(key=itemgetter('name'))
    print_table(projects_data, ['name', 'description'])
