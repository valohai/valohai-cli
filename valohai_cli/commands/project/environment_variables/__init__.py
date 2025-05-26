import click

from valohai_cli.plugin_cli import PluginCLI


@click.command(cls=PluginCLI, commands_module="valohai_cli.commands.project.environment_variables")
def environment_variables() -> None:
    """
    Project environment variable related commands.
    """
