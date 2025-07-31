from __future__ import annotations

import os

import click
from valohai.internals.merge import python_to_yaml_merge_strategy
from valohai.internals.yaml import parse_config_from_source
from valohai.yaml import config_to_yaml
from valohai_yaml.objs.config import Config

from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.models.project import Project


@click.command()
@click.option("--yaml", default=None, help="Path to the YAML file to write to.")
@click.argument(
    "filenames",
    nargs=-1,
    type=click.Path(file_okay=True, exists=True, dir_okay=False),
    required=True,
)
def step(filenames: list[str], yaml: str | None) -> None:
    """
    Update a step config(s) in valohai.yaml based on Python source file(s).

    Example:

        vh yaml step hello.py

    :param filenames: Path(s) of the Python source code files.
    """
    project = get_project()
    if project is None:
        info("no project linked - assuming files are in current directory.")
        project = Project(data={}, directory=os.getcwd())
        project.name = "YAML command simulated project"

    config_path = project.get_config_filename(yaml_path=yaml)
    yaml = yaml or project.get_yaml_path()

    for source_path in filenames:
        if not os.path.isfile(config_path):
            update_yaml_from_source(source_path, project, yaml)
            info(f"{yaml} generated.")
            create_or_update_requirements(project)
        elif yaml_needs_update(source_path, project, yaml):
            update_yaml_from_source(source_path, project, yaml)
            info(f"{yaml} updated.")
            create_or_update_requirements(project)
        else:
            info(f"{yaml} already up-to-date.")


def get_current_config(project: Project, yaml_file: str | None = None) -> Config | None:
    try:
        return project.get_config(yaml_path=yaml_file)
    except FileNotFoundError:
        return None


def get_updated_config(source_path: str, project: Project, yaml_file: str | None = None) -> Config:
    """Opens the old valohai.yaml, parses source Python file and merges the resulting config to the old

    Call to valohai.prepare() will contain step name, parameters and inputs.
    We use the AST parser to parse those from the Python source code file and
    return the merged config.

    :param source_path: Path of the Python source code file
    :param project: Currently linked Valohai project

    """
    old_config = get_current_config(project, yaml_file)
    new_config = parse_config_from_source(source_path, project.get_config_filename(yaml_file))
    if old_config:
        return old_config.merge_with(new_config, python_to_yaml_merge_strategy)
    assert isinstance(new_config, Config)
    return new_config


def update_yaml_from_source(source_path: str, project: Project, yaml_file: str | None) -> bool:
    """Updates valohai.yaml by parsing the source code file for a call to valohai.prepare()

    Call to valohai.prepare() will contain step name, parameters and inputs.
    We use the AST parser to parse those from the Python source code file and
    update (or generate) valohai.yaml accordingly.

    :param source_path: Path of the Python source code file
    :param project: Currently linked Valohai project

    """
    old_config = get_current_config(project, yaml_file)
    new_config = get_updated_config(source_path, project, yaml_file)
    if old_config != new_config:
        with open(project.get_config_filename(yaml_path=yaml_file), "w") as out_file:
            out_file.write(config_to_yaml(new_config))
        return True
    return False


def yaml_needs_update(source_path: str, project: Project, yaml_file: str | None) -> bool:
    """Checks if valohai.yaml needs updating based on source Python code.

    Call to valohai.prepare() will contain step name, parameters and inputs.
    We use the AST parser to parse those from the Python source code file and
    see if valohai.yaml needs updating.

    :param source_path: Path of the Python source code file
    :param project: Currently linked Valohai project

    """
    old_config = get_current_config(project, yaml_file)
    new_config = get_updated_config(source_path, project, yaml_file)

    if not old_config or not new_config:
        return True

    return bool(old_config.serialize() != new_config.serialize())


def create_or_update_requirements(project: Project) -> None:
    """
    Makes sure valohai-utils is in requirements.txt file
    or creates a new requirements.txt with valohai-utils.

    :param project: Currently linked Valohai project
    """

    requirements_path = os.path.join(project.directory, "requirements.txt")

    requirements_lines = []
    if os.path.isfile(requirements_path):
        with open(requirements_path) as requirements:
            requirements_lines = list(requirements)

    if not any("valohai-utils" in line for line in requirements_lines):
        if requirements_lines and "\n" not in requirements_lines[-1]:
            # last line didn't end with a newline, so add one now
            requirements_lines.append("\n")
        requirements_lines.append("valohai-utils\n")
        with open(requirements_path, "w") as requirements:
            requirements.write("".join(requirements_lines))
        info("valohai-utils added to requirements.txt")
