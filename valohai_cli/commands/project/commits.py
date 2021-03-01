import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.git import get_current_commit
from valohai_cli.table import print_table


@click.command()
def commits():
    """
    List the commits for the linked project.
    """
    project = get_project(require=True)
    commits_data = request('get', f'/api/v0/projects/{project.id}/commits/').json()
    try:
        current_commit = get_current_commit(project.directory)
    except:
        current_commit = None

    # Filter out ad-hoc executions (and remove the adhocness marker)
    commits_data = [commit for commit in commits_data if not commit.pop('adhoc', False)]

    # Mark the current commit
    for commit in commits_data:
        if commit['identifier'] == current_commit:
            commit['identifier'] += ' (current)'

    print_table(commits_data)
