from valohai_yaml.objs import Config

from valohai_cli.utils.matching import match_from_list_with_error


def match_pipeline(config: Config, pipeline_name: str) -> str:
    """
    Take a pipeline name and try and match it to the configs pipelines.
    Returns the match if there is only one option.
    """
    return match_from_list_with_error(
        options=list(config.pipelines),
        input=pipeline_name,
        noun="pipeline",
        param_hint="pipeline",
    )
