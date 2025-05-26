from __future__ import annotations

from typing import Any

import click
from click.exceptions import Exit

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.exceptions import APINotFoundError
from valohai_cli.messages import error, success


@click.command()
@click.argument("names", metavar="NAME", nargs=-1, required=True)
def delete(*, names: list[str]) -> Any:
    """
    Delete one or more environment variables.
    """

    project = get_project(require=True)
    fail = False
    for name in names:
        payload = {"name": name}

        try:
            request(method="delete", url=f"/api/v0/projects/{project.id}/environment_variable/", json=payload)
        except APINotFoundError:  # pragma: no cover
            error(f"Environment variable ({name}) not found in {project.name}")
            fail = True
        else:
            success(f"Successfully deleted environment variable {name} from {project.name}")

    if fail:
        raise Exit(1)
