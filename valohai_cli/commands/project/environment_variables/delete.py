from typing import Any

import click
from click.exceptions import Exit

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import error, success


@click.command()
@click.option('--name', '-n', 'name', multiple=False, help='Name of environment variable')
def delete(
        *,
        name: str
) -> Any:
    """
    Delete an environment variable
    """

    project = get_project(require=True)
    payload = {"name": name}

    try:
        request(
            method='delete',
            url=f'/api/v0/projects/{project.id}/environment_variable/',
            json=payload
        )
    except Exception:
        error(f"Environment variable ({name}) not found in {project.name}")
        raise Exit(1)

    success(f"Succesfully deleted environment variable {name} from {project.name}")
