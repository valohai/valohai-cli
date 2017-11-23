import click

from valohai_cli.consts import yes_option
from valohai_cli.settings import settings


@click.command()
@yes_option
def logout(yes):
    """Remove local authentication token."""
    user = settings.get('user')
    token = settings.get('token')
    if not (user or token):
        click.echo('You\'re not logged in.')
        return

    if not yes:
        user = settings['user']
        host = settings['host']
        message = (
            'You are logged in as {username} (on {host}).\n'
            'Are you sure you wish to remove the authentication token?'
        ).format(username=user['username'], host=host)
        click.confirm(message, abort=True)
    settings.update(host=None, user=None, token=None)
    settings.save()
    click.secho('Logged out.', fg='green', bold=True)
