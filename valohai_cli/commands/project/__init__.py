import click

from valohai_cli.plugin_cli import PluginCLI


@click.command(cls=PluginCLI, commands_module='valohai_cli.commands.project')  # type: ignore[call-arg]
def project() -> None:
    """
    Project-related commands.
    """
