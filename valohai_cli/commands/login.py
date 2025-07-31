from __future__ import annotations

from urllib.parse import urljoin, urlparse

import click
from click.exceptions import Exit

from valohai_cli import __version__
from valohai_cli.api import APISession
from valohai_cli.consts import default_app_host, yes_option
from valohai_cli.exceptions import APIError
from valohai_cli.messages import banner, error, info, success, warn
from valohai_cli.settings import settings

TOKEN_LOGIN_HELP = """
Oops!
The error code "{code}" indicates username + password authentication is not possible.
Use a login token instead:
 1. Log in on {host}
 2. Visit {token_url} to generate an authentication token
 3. Once you have an authentication token, paste it below and we'll try it out.
""".strip()


@click.command()
@click.option(
    "--username",
    "-u",
    envvar="VALOHAI_USERNAME",
    help="Your Valohai username",
)
@click.option(
    "--password",
    "-p",
    envvar="VALOHAI_PASSWORD",
    help="Your Valohai password",
)
@click.option(
    "--token",
    "-t",
    envvar="VALOHAI_TOKEN",
    help="A Valohai API token (instead of username and password)",
)
@click.option(
    "--host",
    "-h",
    help="Valohai host to login on (for private installations)",
)
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=True,
    help="Whether to verify SSL connections (this setting is persisted)",
)
@click.option(
    "--ca-file",
    help="Path to bundle file or directory with trusted SSL certificates (this setting is persisted)",
)
@yes_option
def login(
    username: str,
    password: str,
    token: str | None,
    host: str | None,
    yes: bool,
    verify_ssl: bool | str,
    ca_file: str | None,
) -> None:
    """Log in into Valohai."""
    if settings.user and settings.token:
        current_username = settings.user["username"]
        current_host = settings.host
        if not yes:
            click.confirm(
                (
                    f"You are already logged in as {current_username} on {current_host}.\n"
                    "Are you sure you wish to acquire a new token?"
                ),
                abort=True,
            )
        else:
            info(f"--yes set: ignoring pre-existing login for {current_username} on {current_host}")

    if not (token or username or password or host):
        # Don't show the banner if this seems like a non-interactive login.
        click.secho(f"Welcome to Valohai CLI {__version__}!", bold=True)

    if ca_file and not verify_ssl:
        error("You cannot specify a CA file and not verify SSL connections.")
        raise Exit(1)

    # Since `requests` allows `verify` to be a boolean or a string, this is all we really need to do.
    verify_ssl = ca_file or verify_ssl

    host = validate_host(host)
    if token:
        if username or password:
            error("Token is mutually exclusive with username/password")
            raise Exit(1)
        click.echo(f"Using token {token[:5]}... to log in.")
    else:
        token = do_user_pass_login(
            host=host,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
        )

    user_data = verify_token(host=host, token=token, verify_ssl=verify_ssl)
    settings.persistence.update(
        host=host,
        user=user_data,
        token=token,
        verify_ssl=verify_ssl,
    )
    settings.persistence.save()
    success(f"Logged in. Hey {user_data.get('username', 'there')}!")
    if not verify_ssl:
        warn("SSL verification is off. This may leave you vulnerable to man-in-the-middle attacks.")


def verify_token(*, host: str, token: str, verify_ssl: bool | str = True) -> dict:
    click.echo(f"Verifying API token on {host}...")
    with APISession(host, token, verify_ssl=verify_ssl) as sess:
        return sess.get("/api/v0/users/me/").json()


def do_user_pass_login(
    *,
    host: str,
    username: str | None = None,
    password: str | None = None,
    verify_ssl: bool | str = True,
) -> str:
    click.echo(f"\nIf you don't yet have an account, please create one at {host} first.\n")
    if not username:
        username = click.prompt(f"{host} - Username").strip()
    else:
        click.echo(f"Username: {username}")
    if not password:
        password = click.prompt(f"{username} on {host} - Password", hide_input=True)
    click.echo(f"Retrieving API token from {host}...")
    with APISession(host, verify_ssl=verify_ssl) as sess:
        try:
            token_data = sess.post(
                "/api/v0/get-token/",
                data={
                    "username": username,
                    "password": password,
                },
            ).json()
            return str(token_data["token"])
        except APIError as ae:
            if ae.code in ("has_external_identity", "has_2fa"):
                return do_interactive_token_login(
                    host=host,
                    verify_ssl=verify_ssl,
                    login_error_code=ae.code,
                )
            raise


def do_interactive_token_login(
    *,
    host: str,
    verify_ssl: bool | str = True,
    login_error_code: str | None = None,
) -> str:
    banner(
        TOKEN_LOGIN_HELP.format(
            code=login_error_code or "(unknown)",
            host=click.style(host, bold=True),
            token_url=click.style(urljoin(host, "/auth/tokens/"), bold=True),
        ),
    )
    while True:
        token = click.prompt("Enter generated token", hide_input=True)
        try:
            verify_token(host=host, token=token, verify_ssl=verify_ssl)
        except APIError as ae:
            error(f"That didn't work: {ae}")
            continue
        return token


def validate_host(host: str | None) -> str:
    default_host = (
        settings.overrides.get("host")  # from the top-level CLI (or envvar) ...
        or default_app_host  # ... or the global default
    )
    while True:
        if not host:
            host = click.prompt(
                f"Login hostname? (You can just also accept the default {default_host} by leaving this empty.) ",
                default=default_host,
                prompt_suffix=" ",
                show_default=False,
            )
        parsed_host = urlparse(host)
        if parsed_host.scheme not in ("http", "https"):
            error(f"The hostname {host} is not properly formed missing http:// or https://")
            host = None
            continue
        assert isinstance(host, str)
        return host
