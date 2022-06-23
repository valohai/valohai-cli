import click

from valohai_cli.plugin_cli import PluginCLI


@click.command(cls=PluginCLI, commands_module='valohai_cli.commands.data')
def data() -> None:
    """
    Data-related commands.
    """
