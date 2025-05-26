from __future__ import annotations

import re
from typing import Any

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import success, warn

VALID_ENVVAR_NAME_RE = re.compile(r"^[a-z0-9_-]+$", re.I)


def parse_env_variable(s: str) -> tuple[str, str]:
    """
    Parse an environment variable string of the form NAME=VALUE.
    """
    if "=" not in s:
        raise click.BadParameter("Environment variable must be in the form NAME=VALUE")
    key, _, value = s.partition("=")
    key = key.strip()
    if not VALID_ENVVAR_NAME_RE.match(key):
        raise click.BadParameter(
            f"Environment variable name must be alphanumeric-and-dashes-and-underscores, got {key}",
        )
    return key, value.strip()


@click.command()
@click.argument(
    "environment_variables",
    metavar="NAME=VALUE",
    nargs=-1,
    required=True,
    type=parse_env_variable,
)
@click.option("--secret/--public", help="Set environment variable as a secret. Default value is --public")
def create(
    *,
    environment_variables: list[tuple[str, str]],
    secret: bool,
) -> Any:
    """
    Add an environment variable to a project
    """
    project = get_project(require=True)

    if not environment_variables:  # pragma: no cover
        warn("Nothing to do.")
        return

    for key, value in environment_variables:
        payload = {
            "name": key,
            "value": value,
            "secret": secret,
        }

        request(
            method="post",
            url=f"/api/v0/projects/{project.id}/environment_variable/",
            json=payload,
        )

    if len(environment_variables) == 1:
        success(f"Added environment variable {environment_variables[0][0]} to project {project.name}.")
    else:
        success(f"Added {len(environment_variables)} environment variables to project {project.name}.")
