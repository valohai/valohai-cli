import click
from click.exceptions import Exit

from valohai_cli import __version__
from valohai_cli.api import APISession
from valohai_cli.consts import yes_option, default_app_host
from valohai_cli.messages import success, error, info
from valohai_cli.settings import settings


@click.command()
@click.option('--username', '-u', envvar='VALOHAI_USERNAME')
@click.option('--password', '-p', envvar='VALOHAI_PASSWORD')
@click.option('--token', '-t', envvar='VALOHAI_TOKEN')
@click.option('--host', '-h', default=default_app_host)
@yes_option
def login(username, password, token, host, yes):
    """Log in into Valohai."""
    if settings.user and settings.token:
        user = settings.user
        current_username = user['username']
        if not yes:
            message = (
                'You are already logged in as {username}.\n'
                'Are you sure you wish to acquire a new token?'
            ).format(username=current_username)
            click.confirm(message, abort=True)
        else:
            info('--yes set: ignoring pre-existing login for {username}'.format(
                username=current_username,
            ))

    if token:
        if username or password:
            error('Token is mutually exclusive with username/password')
            raise Exit(1)
        click.echo('Using token {token_prefix}... to log in.'.format(token_prefix=token[:5]))
    else:
        if not (username or password):
            click.secho('Welcome to Valohai CLI {version}!'.format(version=__version__), bold=True)
            click.echo('\nIf you don\'t yet have an account, please create one at {host} first.\n'.format(host=host))

        if not username:
            username = click.prompt('Username').strip()
        else:
            click.echo('Username: {}'.format(username))

        if not password:
            password = click.prompt('Password', hide_input=True)

        click.echo('Retrieving API token...')

        with APISession(host) as sess:
            token_data = sess.post('/api/v0/get-token/', data={'username': username, 'password': password}).json()
            token = token_data['token']

    click.echo('Verifying API token...')

    with APISession(host, token) as sess:
        user_data = sess.get('/api/v0/users/me/').json()
    settings.persistence.update(host=host, user=user_data, token=token)
    settings.persistence.save()
    success('Logged in. Hey {name}!'.format(name=user_data.get('username', 'there')))
