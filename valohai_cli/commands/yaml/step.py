import os
from typing import Optional

import click
from valohai.internals.yaml import parse_config_from_source
from valohai.yaml import config_to_yaml
from valohai_yaml.objs import Config

from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.models.project import Project


@click.command()
@click.argument('filenames', nargs=-1, type=click.Path(file_okay=True, exists=True, dir_okay=False), required=True)
def step(filenames):
    """
    Update a step config(s) in valohai.yaml based on Python source file(s).

    Example:

        vh yaml step hello.py

    :param filenames: Path(s) of the Python source code files.
    """
    project = get_project()
    config_path = project.get_config_filename()

    for source_path in filenames:
        if not os.path.isfile(config_path):
            update_yaml_from_source(source_path, project)
            info("valohai.yaml generated.")
        elif yaml_needs_update(source_path, project):
            update_yaml_from_source(source_path, project)
            info("valohai.yaml updated.")
        else:
            info("valohai.yaml already up-to-date.")


def get_current_config(project: Project) -> Optional[Config]:
    try:
        return project.get_config()
    except FileNotFoundError:
        return None


def get_updated_config(source_path: str, project: Project) -> Config:
    """Opens the old valohai.yaml, parses source Python file and merges the resulting config to the old

    Call to valohai.prepare() will contain step name, parameters and inputs.
    We use the AST parser to parse those from the Python source code file and
    return the merged config.

    :param source_path: Path of the Python source code file
    :param project: Currently linked Valohai project

    """
    old_config = get_current_config(project)
    new_config = parse_config_from_source(source_path, project.get_config_filename())
    if old_config:
        return old_config.merge_with(new_config)
    return new_config


def update_yaml_from_source(source_path: str, project: Project) -> bool:
    """Updates valohai.yaml by parsing the source code file for a call to valohai.prepare()

    Call to valohai.prepare() will contain step name, parameters and inputs.
    We use the AST parser to parse those from the Python source code file and
    update (or generate) valohai.yaml accordingly.

    :param source_path: Path of the Python source code file
    :param project: Currently linked Valohai project

    """
    old_config = get_current_config(project)
    new_config = get_updated_config(source_path, project)
    if old_config != new_config:
        with open(project.get_config_filename(), 'w') as out_file:
            out_file.write(config_to_yaml(new_config))
        return True
    return False

def yaml_needs_update(source_path: str, project: Project) -> bool:
    """Checks if valohai.yaml needs updating based on source Python code.

    Call to valohai.prepare() will contain step name, parameters and inputs.
    We use the AST parser to parse those from the Python source code file and
    see if valohai.yaml needs updating.

    :param source_path: Path of the Python source code file
    :param project: Currently linked Valohai project

    """
    old_config = get_current_config(project)
    new_config = get_updated_config(source_path, project)

    if not old_config or not new_config:
        return True

    return old_config.serialize() != new_config.serialize()
