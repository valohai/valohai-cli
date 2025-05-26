from __future__ import annotations

from typing import Any

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table


@click.command()
def list() -> Any:
    """
    List environment variables of a project
    """

    project = get_project(require=True)
    data = request(method="get", url=f"/api/v0/projects/{project.id}/").json()["environment_variables"]

    if settings.output_format == "json":
        return print_json(data)

    if not data:  # pragma: no cover
        info(f"{project}: No environment variables.")
        return

    formatted_envvars = [
        {
            "name": name,
            "value": "****" if info["secret"] else info["value"],
            "secret": info["secret"],
        }
        for name, info in sorted(data.items())
    ]

    print_table(
        formatted_envvars,
        columns=["name", "value", "secret"],
        headers=["Name", "Value", "Secret"],
    )
