import click
from click import Context

from typing import List, Any

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import success


@click.command()
@click.option('--var', '-v', 'environment_variable', multiple=False, help='Add a environment variable (NAME=VALUE). May be repeated.')
@click.option('--secret/--public', help='Set environment variable as a secret. Default value is --public')
@click.pass_context
def create(
        ctx: click.Context,
        *,
        environment_variable: str,
        secret: bool
    ) -> Any:
    """
    Add a environment variable to a project
    """
    key, _, value = environment_variable.partition('=')
    key = key.strip()

    payload = {
        "name": key,
        "value": value.strip(),
        "secret": secret
    }

    project = get_project(require=True)
    request(
        method='post',
        url=f'/api/v0/projects/{project.id}/environment_variable/',
        json=payload
    ).json()

    success(f"Added environment variables to project.")
