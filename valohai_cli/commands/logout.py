import click

from valohai_cli.consts import yes_option
from valohai_cli.messages import success
from valohai_cli.settings import settings


@click.command()
@yes_option
def logout(yes):
    """Remove local authentication token."""
    user = settings.user
    token = settings.token
    if not (user or token):
        click.echo('You\'re not logged in.')
        return

    if not yes:
        message = (
            'You are logged in as {username} (on {host}).\n'
            'Are you sure you wish to remove the authentication token?'
        ).format(username=user['username'], host=settings.host)
        click.confirm(message, abort=True)
    settings.persistence.update(host=None, user=None, token=None)
    settings.persistence.save()
    success('Logged out.')
