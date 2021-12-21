import click
from valohai_yaml.objs import Config

from valohai_cli.utils import match_prefix


def match_pipeline(config: Config, pipeline_name: str) -> str:
    """
    Take a pipeline name and try and match it to the configs pipelines.
    Returns the match if there is only one option.
    """
    if pipeline_name in config.pipelines:
        return pipeline_name
    matching_pipelines = match_prefix(config.pipelines, pipeline_name, return_unique=False)
    if not matching_pipelines:
        raise click.BadParameter(
            '"{pipeline}" is not a known pipeline (try one of {pipelines})'.format(
                pipeline=pipeline_name,
                pipelines=', '.join(click.style(t, bold=True) for t in sorted(config.pipelines))
            ), param_hint='pipeline')
    if len(matching_pipelines) > 1:
        raise click.BadParameter(
            '"{pipeline}" is ambiguous.\nIt matches {matches}.\nKnown pipelines are {pipelines}.'.format(
                pipeline=pipeline_name,
                matches=', '.join(click.style(t, bold=True) for t in sorted(matching_pipelines)),
                pipelines=', '.join(click.style(t, bold=True) for t in sorted(config.pipelines)),
            ), param_hint='pipeline')
    return str(matching_pipelines[0])
