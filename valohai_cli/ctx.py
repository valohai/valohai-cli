from __future__ import annotations

from typing import Literal, Union, overload

import click

from valohai_cli.exceptions import NoProject
from valohai_cli.messages import success
from valohai_cli.models.project import Project
from valohai_cli.models.remote_project import RemoteProject
from valohai_cli.settings import settings
from valohai_cli.utils import get_project_directory

ProjectOrRemoteProject = Union[RemoteProject, Project]


@overload
def get_project(dir: str | None = None, require: Literal[True] = True) -> ProjectOrRemoteProject: ...


@overload
def get_project(
    dir: str | None = None,
    require: Literal[False] = False,
) -> ProjectOrRemoteProject | None: ...


def get_project(dir: str | None = None, require: bool = False) -> ProjectOrRemoteProject | None:
    """
    Get the Valohai project object for a directory context.

    The directory tree is walked upwards to find an actual linked directory.

    :param dir: Directory (defaults to cwd)
    :param require: Raise an exception if no project is found
    :return: Project object, or None.
    """
    dir = dir or get_project_directory()
    project = settings.get_project(dir)
    if not project and require:
        raise NoProject(f"No project is linked to {dir}")
    return project


def set_project_link(dir: str, project: dict, inform: bool = False) -> None:
    settings.set_project_link(dir, project)
    if inform:
        success(f'Linked {click.style(dir, bold=True)} to {click.style(project["name"], bold=True)}.')
