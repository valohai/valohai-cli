from valohai_yaml.objs.config import Config

from valohai_cli.utils.matching import match_from_list_with_error


def match_step(config: Config, step: str) -> str:
    return match_from_list_with_error(
        options=list(config.steps),
        input=step,
        noun="step",
        param_hint="step",
    )
