import click

from valohai_cli.utils import match_prefix


def match_step(config, step):
    if step in config.steps:
        return step
    step_matches = match_prefix(config.steps, step, return_unique=False)
    if not step_matches:
        raise click.BadParameter(
            '"{step}" is not a known step (try one of {steps})'.format(
                step=step,
                steps=', '.join(click.style(t, bold=True) for t in sorted(config.steps))
            ), param_hint='step')
    if len(step_matches) > 1:
        raise click.BadParameter(
            '"{step}" is ambiguous.\nIt matches {matches}.\nKnown steps are {steps}.'.format(
                step=step,
                matches=', '.join(click.style(t, bold=True) for t in sorted(step_matches)),
                steps=', '.join(click.style(t, bold=True) for t in sorted(config.steps)),
            ), param_hint='step')
    return step_matches[0]
