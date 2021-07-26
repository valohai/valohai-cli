from typing import List

import click
from valohai.internals.pipeline import get_pipeline_from_source
from valohai.yaml import config_to_yaml
from valohai_yaml.objs.config import Config

from valohai_cli.ctx import get_project
from valohai_cli.exceptions import ConfigurationError
from valohai_cli.messages import info
from valohai_cli.models.project import Project


@click.command()
@click.argument('filenames', nargs=-1, type=click.Path(file_okay=True, exists=True, dir_okay=False), required=True)
def pipeline(filenames: List[str]) -> None:
    """
    Update a pipeline config(s) in valohai.yaml based on Python source file(s).
    Python source file is expected to have def main(config: Config) -> Pipeline

    Example:

        vh yaml pipeline mypipeline.py

    :param filenames: Path(s) of the Python source code files.
    """
    project = get_project(require=True)

    for source_path in filenames:
        if yaml_needs_update(source_path, project):
            update_yaml_from_source(source_path, project)
            info("valohai.yaml updated.")
        else:
            info("valohai.yaml already up-to-date.")


def get_current_config(project: Project) -> Config:
    try:
        return project.get_config()
    except FileNotFoundError as fnfe:
        valohai_yaml_name = project.get_config_filename()
        raise ConfigurationError(
            f"Did not find {valohai_yaml_name}. "
            f"Can't create a pipeline without preconfigured steps."
        ) from fnfe


def get_updated_config(source_path: str, project: Project) -> Config:
    """Gets pipeline definition from the source_path and merges it with existing config

    :param source_path: Path of the Python source code file containing the pipeline definition
    :param project: Currently linked Valohai project

    """
    old_config = get_current_config(project)
    new_config = get_pipeline_from_source(source_path, old_config)
    return old_config.merge_with(new_config)


def update_yaml_from_source(source_path: str, project: Project) -> bool:
    """Updates valohai.yaml by parsing the pipeline definition from the source_path

    :param source_path: Path of the Python source code file containing the pipeline definition
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

    :param source_path: Path of the Python source code file containing the pipeline definition
    :param project: Currently linked Valohai project

    """
    old_config = get_current_config(project)
    new_config = get_updated_config(source_path, project)
    return bool(old_config.serialize() != new_config.serialize())
