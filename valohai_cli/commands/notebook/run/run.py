from __future__ import annotations

from typing import Any

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import success


@click.command()
@click.option(
    "--environment",
    "-e",
    help="Environment UUID or slug to run the execution in.",
    required=True,
)
@click.option(
    "--image",
    "-i",
    help="Docker image to use for the notebook execution.",
    required=True,
)
@click.pass_context
def run(
    ctx: click.Context,  # noqa: ARG001
    *,
    environment: str,
    image: str,
) -> None:
    """
    Start a notebook execution.
    """
    project = get_project(require=True)
    assert project

    start_execution(environment, project.id, image)


def start_execution(
    environment_id_or_slug: str,
    project_id: str,
    image: str,
) -> None:
    payload: dict[str, Any] = {
        "environment": environment_id_or_slug,
        "project": project_id,
        "image": image,
    }
    response = request(
        "post",
        "/api/v0/notebook-executions/",
        json=payload,
    ).json()

    success(f"Notebook execution {response.get('counter')} queued. See {response.get('urls').get('display')}")
