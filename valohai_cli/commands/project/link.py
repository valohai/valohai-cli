import contextlib
from typing import Any, List, Optional, Sequence

import click

from valohai_cli.api import request
from valohai_cli.commands.project.create import create_project, prompt_for_owner
from valohai_cli.consts import yes_option
from valohai_cli.ctx import get_project, set_project_link
from valohai_cli.messages import warn
from valohai_cli.utils import get_project_directory
from valohai_cli.utils.cli_utils import prompt_from_list


class NewProjectInstead(Exception):
    pass


def filter_projects(projects: Sequence[dict], spec: str) -> List[dict]:
    spec = str(spec).lower()
    return [
        project for project in projects if project["id"].lower() == spec or project["name"].lower() == spec
    ]


def choose_project(dir: str, spec: Optional[str] = None) -> Optional[dict]:
    """
    Choose a project, possibly interactively.

    :param dir: Directory (only used for prompts)
    :param spec: An optional search string
    :return: project object or None
    """
    projects: List[dict] = request("get", "/api/v0/projects/", params={"limit": "1000"}).json()["results"]
    if not projects:
        if click.confirm("You don't have any projects. Create one instead?"):
            raise NewProjectInstead()
        return None

    if spec:
        projects = filter_projects(projects, spec)
        if not projects:
            warn(f"No projects match {spec}")
            return None
        if len(projects) == 1:
            return projects[0]

    def nonlist_validator(answer: str) -> Any:
        if answer.startswith("c"):
            raise NewProjectInstead()

    prompt = (
        f"Which project would you like to link with {click.style(dir, bold=True)}?\n"
        f"Enter [c] to create a new project."
    )
    has_multiple_owners = len({p.get("owner", {}).get("id") for p in projects}) > 1

    def project_name_formatter(project: dict) -> str:
        name: str = project["name"]
        with contextlib.suppress(Exception):
            if has_multiple_owners:
                dim_owner = click.style(project["owner"]["username"] + "/", dim=True)
                return f"{dim_owner}{name}"
        return name

    projects.sort(key=lambda project: project_name_formatter(project).lower())
    return prompt_from_list(projects, prompt, nonlist_validator, name_formatter=project_name_formatter)


@click.command()
@click.argument("project", default=None, required=False)
@yes_option
def link(project: Optional[str], yes: bool) -> Any:
    """
    Link a directory with a Valohai project.
    """
    dir = get_project_directory()
    current_project = get_project(dir)
    if current_project and not yes:
        click.confirm(
            (
                f"{click.style(current_project.directory, bold=True)} is already linked to "
                f"project {click.style(current_project.name, bold=True)}; continue?"
            ),
            abort=True,
        )
    try:
        project_obj = choose_project(dir, spec=project)
        if not project_obj:
            return 1
        set_project_link(dir, project_obj, inform=True)
    except NewProjectInstead:
        name = click.prompt("Name the new project")
        owner = prompt_for_owner(command_prompt="Owner")
        if name:
            create_project(dir, name, yes=yes, owner=owner)
