from __future__ import annotations

import json

import click
from valohai_yaml.pipelines.conversion import PipelineConverter

from valohai_cli.commands.pipeline.run.utils import match_pipeline
from valohai_cli.ctx import get_project


@click.command(name="convert-to-api")
@click.argument(
    "name",
    required=True,
    metavar="PIPELINE-NAME",
)
@click.option(
    "--commit",
    "-c",
    metavar="SHA",
    help="The commit to use in the API call.",
    required=True,
)
@click.option(
    "--yaml",
    default=None,
    help="The path to the configuration YAML file (valohai.yaml) to use.",
)
@click.option(
    "--indent",
    type=int,
    default=2,
    help="JSON indentation level. Use 0 for compact output.",
)
def convert_to_api(
    *,
    name: str,
    commit: str,
    yaml: str | None,
    indent: int,
) -> None:
    """
    Convert a pipeline configuration to API format (JSON).

    This command reads a pipeline from your valohai.yaml configuration
    and outputs the API-compatible JSON payload that would be sent when
    running the pipeline.
    """
    project = get_project(require=True)
    assert project

    config = project.get_config(commit_identifier=commit if project.is_remote else None, yaml_path=yaml)
    pipeline = config.pipelines[match_pipeline(config, name)]
    converted_pipeline = PipelineConverter(
        config=config,
        commit_identifier=commit,
        parameter_arguments={},
    ).convert_pipeline(pipeline)

    if indent == 0:
        output = json.dumps(converted_pipeline, separators=(',', ':'))
    else:
        output = json.dumps(converted_pipeline, indent=indent)

    click.echo(output)
