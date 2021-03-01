import sys

import click
from click.exceptions import Exit

from valohai_cli import __version__
from valohai_cli.api import APISession
from valohai_cli.consts import default_app_host, yes_option
from valohai_cli.exceptions import APIError
from valohai_cli.messages import error, info, success, banner
from valohai_cli.settings import settings


TOKEN_LOGIN_HELP = '''
Oops!
The error code "{code}" indicates username + password authentication is not possible.
Use a login token instead:
 1. Log in on {host}
 2. Visit {host}auth/tokens/ to generate an authentication token
 3. Once you have an authentication token, log in with:
    {command}
'''.strip()


@click.command()
@click.option('--username', '-u', envvar='VALOHAI_USERNAME', help='Your Valohai username')
@click.option('--password', '-p', envvar='VALOHAI_PASSWORD', help='Your Valohai password')
@click.option('--token', '-t', envvar='VALOHAI_TOKEN', help='A Valohai API token (instead of username and password)')
@click.option('--host', '-h', help='Valohai host to login on (for private installations)')
@yes_option
def login(username, password, token, host, yes):
    """Log in into Valohai."""
    host = (
        host  # Explicitly set for this command, ...
        or settings.overrides.get('host')  # ... or from the top-level CLI (or envvar) ...
        or default_app_host  # ... or the global default
    )
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
            click.secho(f'Welcome to Valohai CLI {__version__}!', bold=True)
            click.echo(f'\nIf you don\'t yet have an account, please create one at {host} first.\n')

        if not username:
            username = click.prompt('Username').strip()
        else:
            click.echo(f'Username: {username}')

        if not password:
            password = click.prompt('Password', hide_input=True)

        click.echo('Retrieving API token...')

        with APISession(host) as sess:
            try:
                token_data = sess.post('/api/v0/get-token/', data={
                    'username': username,
                    'password': password,
                }).json()
                token = token_data['token']
            except APIError as ae:
                code = ae.code
                if code in ('has_external_identity', 'has_2fa'):
                    command = 'vh login --token TOKEN_HERE '
                    if host != default_app_host:
                        command += f'--host {host}'
                    banner(TOKEN_LOGIN_HELP.format(code=code, host=host, command=command))
                raise

    click.echo('Verifying API token...')

    with APISession(host, token) as sess:
        user_data = sess.get('/api/v0/users/me/').json()
    settings.persistence.update(host=host, user=user_data, token=token)
    settings.persistence.save()
    success('Logged in. Hey {name}!'.format(name=user_data.get('username', 'there')))
