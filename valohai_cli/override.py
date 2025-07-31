from __future__ import annotations

import os

import click

from valohai_cli.consts import default_app_host
from valohai_cli.messages import info
from valohai_cli.settings import settings


def configure_token_login(host: str | None, token: str) -> None:
    settings.overrides["host"] = host or default_app_host
    settings.overrides["user"] = {"id": "<none>", "username": "<logged in via --valohai-token>"}
    settings.overrides["token"] = token


def configure_project_override(project_id: str, mode: str | None, directory: str | None = None) -> None:
    if not directory:
        directory = os.getcwd()
    if not mode:
        yaml_filename = os.path.join(directory, "valohai.yaml")
        if os.path.isfile(yaml_filename):
            info(f"{yaml_filename} exists, assuming local project")
            mode = "local"
        else:
            info(f"{yaml_filename} does not exist, assuming remote project")
            mode = "remote"
    if not settings.set_override_project(project_id, directory=directory, mode=mode):
        raise click.Abort()
