from typing import List, Optional

import click
from valohai.internals.pipeline import get_pipeline_from_source
from valohai.yaml import config_to_yaml

from valohai_cli.ctx import get_project
from valohai_cli.exceptions import ConfigurationError
from valohai_cli.messages import error, info


@click.command()
@click.option('--yaml', default=None, help='Path to the YAML file to update.')
@click.argument(
    "filenames",
    nargs=-1,
    type=click.Path(file_okay=True, exists=True, dir_okay=False),
    required=True,
)
def pipeline(filenames: List[str], yaml: Optional[str]) -> None:
    """
    Update a pipeline config(s) in valohai.yaml based on Python source file(s).
    Python source file is expected to have def main(config: Config) -> Pipeline

    Example:

        vh yaml pipeline mypipeline.py

    :param filenames: Path(s) of the Python source code files.
    """
    project = get_project(require=True)
    yaml_filename = project.get_config_filename(yaml_path=yaml)
    did_update = False
    for source_path in filenames:
        try:
            old_config = project.get_config(yaml_path=yaml)
        except FileNotFoundError as fnfe:
            raise ConfigurationError(
                f"Did not find {yaml_filename}. "
                f"Can't create a pipeline without preconfigured steps."
            ) from fnfe
        try:
            new_config = get_pipeline_from_source(source_path, old_config)
        except Exception:
            error(
                f"Retrieving a new pipeline definition for project {project} for {source_path} failed.\n"
                f"The configuration file in use is {yaml_filename}. "
                f"See the full traceback below."
            )
            raise

        merged_config = old_config.merge_with(new_config)
        if old_config.serialize() != merged_config.serialize():
            with open(yaml_filename, "w") as out_file:
                out_file.write(config_to_yaml(merged_config))
            did_update = True
    if did_update:
        info(f"{yaml_filename} updated.")
    else:
        info(f"{yaml_filename} already up-to-date.")
