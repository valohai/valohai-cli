import click

from valohai_cli.consts import yes_option
from valohai_cli.messages import success
from valohai_cli.settings import settings


@click.command()
@yes_option
def logout(yes: bool) -> None:
    """Remove local authentication token."""
    user = settings.user
    token = settings.token
    if not (user or token):
        click.echo("You're not logged in.")
        return

    if user and not yes:
        click.confirm(
            (
                f'You are logged in as {user["username"]} (on {settings.host}).\n'
                'Are you sure you wish to remove the authentication token?'
            ),
            abort=True,
        )
    settings.persistence.update(host=None, user=None, token=None)
    settings.persistence.save()
    success("Logged out.")
