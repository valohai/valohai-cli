import logging
from typing import Optional

import click

from valohai_cli.consts import default_app_host
from valohai_cli.override import configure_project_override, configure_token_login
from valohai_cli.plugin_cli import RecursiveHelpPluginCLI
from valohai_cli.settings import settings
from valohai_cli.table import TABLE_FORMATS

TABLE_FORMAT_ENVVARS = ["VALOHAI_TABLE_FORMAT", "VALOHAI_OUTPUT_FORMAT"]


@click.command(cls=RecursiveHelpPluginCLI, commands_module="valohai_cli.commands")
@click.option(
    "--debug/--no-debug",
    default=False,
    envvar="VALOHAI_DEBUG",
    help="Enable debug logging.",
)
@click.option(
    "--output-format",
    "--table-format",
    type=click.Choice(TABLE_FORMATS),
    default="human",
    envvar=TABLE_FORMAT_ENVVARS,
    help="Set the output format for various data.",
)
@click.option(
    "--valohai-host",
    envvar="VALOHAI_HOST",
    metavar="URL",
    help=f"Override the Valohai API host (default {default_app_host})",
    show_envvar=True,
)
@click.option(
    "--valohai-token",
    envvar="VALOHAI_TOKEN",
    metavar="SECRET",
    help="Use this Valohai authentication token",
    show_envvar=True,
)
@click.option(
    "--project",
    "project_id",
    envvar="VALOHAI_PROJECT",
    type=click.UUID,
    help="(Advanced) Override the project ID",
    show_envvar=True,
)
@click.option(
    "--project-mode",
    "project_mode",
    envvar="VALOHAI_PROJECT_MODE",
    metavar="local|remote",
    help="(Advanced) When using --project, set the project mode",
    show_envvar=True,
)
@click.option(
    "--project-root",
    "project_root",
    type=click.Path(dir_okay=True, exists=True, file_okay=False),
    metavar="DIR",
    envvar="VALOHAI_PROJECT_ROOT",
    help="(Advanced) When using --project, set the project root directory",
    show_envvar=True,
)
@click.pass_context
def cli(
    ctx: click.Context,
    debug: bool,
    output_format: str,
    valohai_host: Optional[str],
    valohai_token: Optional[str],
    project_id: Optional[str],
    project_mode: Optional[str],
    project_root: Optional[str],
) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    ctx.meta["debug"] = debug
    settings.output_format = output_format
    if valohai_host:
        settings.overrides["host"] = valohai_host
    if valohai_token:
        configure_token_login(host=valohai_host, token=valohai_token)
    if project_id:
        configure_project_override(project_id, mode=project_mode, directory=project_root)
    else:
        if project_mode:
            raise click.UsageError(
                f"--project-mode (currently {project_mode}) must not be set without --project",
            )
        if project_root:
            raise click.UsageError(
                f"--project-root (currently {project_root}) must not be set without --project",
            )


if __name__ == "__main__":
    cli()
