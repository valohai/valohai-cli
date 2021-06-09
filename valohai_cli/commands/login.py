from typing import Optional

import click
from click.exceptions import Exit
from urllib.parse import urlparse

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
def login(username: str, password: str, token: Optional[str], host: Optional[str], yes: bool) -> None:
    """Log in into Valohai."""
    if settings.user and settings.token:
        current_username = settings.user['username']
        current_host = settings.host
        if not yes:
            click.confirm((
                f'You are already logged in as {current_username} on {current_host}.\n'
                'Are you sure you wish to acquire a new token?'
            ), abort=True)
        else:
            info(f'--yes set: ignoring pre-existing login for {current_username} on {current_host}')

    if not (token or username or password or host):
        # Don't show the banner if this seems like a non-interactive login.
        click.secho(f'Welcome to Valohai CLI {__version__}!', bold=True)

    host = validate_host(host)
    if token:
        if username or password:
            error('Token is mutually exclusive with username/password')
            raise Exit(1)
        click.echo(f'Using token {token[:5]}... to log in.')
    else:
        token = do_user_pass_login(host=host, username=username, password=password)

    click.echo(f'Verifying API token on {host}...')

    with APISession(host, token) as sess:
        user_data = sess.get('/api/v0/users/me/').json()
    settings.persistence.update(host=host, user=user_data, token=token)
    settings.persistence.save()
    success(f"Logged in. Hey {user_data.get('username', 'there')}!")


def do_user_pass_login(
    *,
    host: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    click.echo(f'\nIf you don\'t yet have an account, please create one at {host} first.\n')
    if not username:
        username = click.prompt(f'{host} - Username').strip()
    else:
        click.echo(f'Username: {username}')
    if not password:
        password = click.prompt(f'{username} on {host} - Password', hide_input=True)
    click.echo(f'Retrieving API token from {host}...')
    with APISession(host) as sess:
        try:
            token_data = sess.post('/api/v0/get-token/', data={
                'username': username,
                'password': password,
            }).json()
            return str(token_data['token'])
        except APIError as ae:
            code = ae.code
            if code in ('has_external_identity', 'has_2fa'):
                command = 'vh login --token TOKEN_HERE '
                if host != default_app_host:
                    command += f'--host {host}'
                banner(TOKEN_LOGIN_HELP.format(code=code, host=host, command=command))
            raise


def validate_host(host: Optional[str]) -> str:
    default_host = (
        settings.overrides.get('host')  # from the top-level CLI (or envvar) ...
        or default_app_host  # ... or the global default
    )
    while True:
        if not host:
            host = click.prompt(
                f'Login hostname? (You can just also accept the default {default_host} by leaving this empty.) ',
                default=default_host,
                prompt_suffix=' ',
                show_default=False,
            )
        parsed_host = urlparse(host)
        if parsed_host.scheme not in ('http', 'https'):
            error(f'The hostname {host} is not properly formed missing http:// or https://')
            host = None
            continue
        assert isinstance(host, str)
        return host
