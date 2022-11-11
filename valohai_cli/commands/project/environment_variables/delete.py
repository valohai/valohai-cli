import click
from click import Context
from click.exceptions import Exit

from typing import List, Any

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import success, error


@click.command()
@click.option('--name', '-n', 'name', multiple=False, help='Name of environment variable')
@click.pass_context
def delete(
        ctx: click.Context,
        *,
        name: str
    ) -> Any:
    """
    Delete an environment variable
    """
    
    project = get_project(require=True)
    payload = {"name": name}

    try:
        resp = request(
            method='delete',
            url=f'/api/v0/projects/{project.id}/environment_variable/',
            json = payload
        )
    except Exception:
        error(f"Environment variable ({name}) not found in {project.name}")
        raise Exit(1)

    success(f"Succesfully deleted environment variable {name} from {project.name}")
