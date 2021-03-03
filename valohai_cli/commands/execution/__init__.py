import click

from valohai_cli.plugin_cli import PluginCLI


@click.command(cls=PluginCLI, commands_module='valohai_cli.commands.execution')  # type: ignore[call-arg]
def execution() -> None:
    """
    Execution-related commands.
    """
