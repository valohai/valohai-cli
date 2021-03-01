from logging import info, warning

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import success


@click.command()
def fetch():
    """
    Fetch new commits for the linked project.
    """
    project = get_project(require=True)
    resp = request('post', f'/api/v0/projects/{project.id}/fetch/')
    data = resp.json()
    commits = data.get('commits', ())
    if commits:
        for commit in commits:
            success('Fetched: {ref} ({identifier})'.format(ref=commit['ref'], identifier=commit['identifier']))
        success('{n} new commits were fetched!'.format(n=len(commits)))
    else:
        info('No new commits.')
    errors = data.get('errors', ())
    for error in errors:
        warning(error)
