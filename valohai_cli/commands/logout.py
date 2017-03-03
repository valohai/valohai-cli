import click

from valohai_cli.settings import settings


@click.command()
@click.option('--yes/-y')
def logout(yes):
    """Remove local authentication token."""
    user = settings.get('user')
    token = settings.get('token')
    if not (user or token):
        click.echo('You\'re not logged in.')
        return

    if not yes:
        user = settings['user']
        message = (
            'You are logged in as {username}.\n'
            'Are you sure you wish to remove the authentication token?'
        ).format(username=user['username'])
        click.confirm(message, abort=True)
    settings.update(host=None, user=None, token=None)
    settings.save()
    click.secho('Logged out.', fg='green', bold=True)
