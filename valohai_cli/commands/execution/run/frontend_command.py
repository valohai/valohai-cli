import contextlib
from typing import Any, List, Optional

import click

from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.utils import parse_environment_variable_strings
from valohai_cli.utils.commits import create_or_resolve_commit

from .dynamic_run_command import RunCommand
from .utils import match_step

run_epilog = (
    'More detailed help (e.g. how to define parameters and inputs) is available when you have '
    'defined which step to run. For instance, if you have a step called Extract, '
    'try running "vh exec run Extract --help".'
)


@click.command(
    context_settings=dict(ignore_unknown_options=True),
    add_help_option=False,
    epilog=run_epilog,
)
@click.argument('step_name', required=False, metavar='STEP-NAME')
@click.option('--commit', '-c', default=None, metavar='SHA', help='The commit to use. Defaults to the current HEAD.')
@click.option('--environment', '-e', default=None, help='The environment UUID or slug to use (see "vh env")')
@click.option('--image', '-i', default=None, help='Override the Docker image specified in the step.')
@click.option('--title', '-t', default=None, help='Title of the execution.')
@click.option('--watch', '-w', is_flag=True, help='Start "exec watch"ing the execution after it starts.')
@click.option('--open-browser', is_flag=True, help='Open default web browser to execution page after it starts.')
@click.option('--var', '-v', 'environment_variables', multiple=True, help='Add environment variable (NAME=VALUE). May be repeated.')
@click.option('--tag', 'tags', multiple=True, help='Tag the execution. May be repeated.')
@click.option('--sync', '-s', 'download_directory', type=click.Path(file_okay=False), help='Download execution outputs to DIRECTORY.', default=None)
@click.option('--adhoc', '-a', is_flag=True, help='Upload the current state of the working directory, then run it as an ad-hoc execution.')
@click.option('--validate-adhoc/--no-validate-adhoc', help='Enable or disable validation of adhoc packaged code, on by default', default=True)
@click.option('--yaml', default=None, help='The path to the configuration YAML (valohai.yaml) file to use.')
@click.option('--debug-port', type=int)
@click.option('--debug-key-file', type=click.Path(file_okay=True, readable=True, writable=False))
@click.option('--autorestart/--no-autorestart', help='Enable Automatic Restart on Spot Instance Interruption')
@click.argument('args', nargs=-1, type=click.UNPROCESSED, metavar='STEP-OPTIONS...')
@click.pass_context
def run(
    ctx: click.Context,
    *,
    adhoc: bool,
    args: List[str],
    commit: Optional[str],
    yaml: Optional[str],
    download_directory: Optional[str],
    environment: Optional[str],
    environment_variables: List[str],
    image: Optional[str],
    step_name: Optional[str],
    tags: List[str],
    title: Optional[str],
    validate_adhoc: bool,
    watch: bool,
    open_browser: bool,
    debug_port: int,
    debug_key_file: Optional[str],
    autorestart: bool,
) -> Any:
    """
    Start an execution of a step.
    """
    # Having to explicitly compare to `--help` is slightly weird, but it's because of the nested command thing.
    if step_name == '--help' or not step_name:
        click.echo(ctx.get_help(), color=ctx.color)
        print_step_list(ctx, commit)
        ctx.exit()
        return
    project = get_project(require=True)
    project.refresh_details()

    if download_directory and watch:
        raise click.UsageError('Combining --sync and --watch not supported yet.')

    if not commit and project.is_remote:
        # For remote projects, we need to resolve early.
        commit = project.resolve_commit()['identifier']
        info(f'Using remote project {project.name}\'s newest commit {commit}')

    # We need to pass commit=None when adhoc=True to `get_config`, but
    # the further steps do need the real commit identifier from remote,
    # so this is done before `commit` is mangled by `create_adhoc_commit`.
    config = project.get_config(commit_identifier=commit, yaml_path=yaml)
    matched_step = match_step(config, step_name)
    step = config.steps[matched_step]

    commit = create_or_resolve_commit(
        project,
        commit=commit,
        adhoc=adhoc,
        validate_adhoc_commit=validate_adhoc,
        yaml_path=yaml,
    )

    runtime_config = {}  # type: dict[str, Any]

    if bool(debug_port) ^ bool(debug_key_file):
        raise click.UsageError(
            "Both or neither of --debug-port and --debug-key-file must be set."
        )
    if debug_port and debug_key_file:
        runtime_config["debug_port"] = debug_port
        with open(debug_key_file, "r") as file:
            key = file.read().strip()
            if not key.startswith("ssh"):
                raise click.UsageError(
                    f"The public key read from {debug_key_file} "
                    f"does not seem valid (it should start with `ssh`)"
                )
        runtime_config["debug_key"] = key
    if autorestart:
        runtime_config["autorestart"] = autorestart

    rc = RunCommand(
        project=project,
        step=step,
        commit=commit,
        environment=environment,
        open_browser=open_browser,
        watch=watch,
        download_directory=download_directory,
        image=image,
        title=title,
        environment_variables=parse_environment_variable_strings(environment_variables),
        tags=tags,
        runtime_config=runtime_config,
    )
    with rc.make_context(rc.name, list(args), parent=ctx) as child_ctx:
        return rc.invoke(child_ctx)


def print_step_list(ctx: click.Context, commit: Optional[str]) -> None:
    with contextlib.suppress(Exception):  # If we fail to extract the step list, it's not that big of a deal.
        config = get_project(require=True).get_config(commit_identifier=commit)
        if config.steps:
            click.secho('\nThese steps are available in the selected commit:\n', color=ctx.color, bold=True)
            for step in sorted(config.steps):
                click.echo(f'   * {step}', color=ctx.color)
