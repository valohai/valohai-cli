import click

from valohai_cli.plugin_cli import PluginCLI


@click.command(cls=PluginCLI, commands_module='valohai_cli.commands')
@click.option('--debug/--no-debug', default=False, envvar='VALOHAI_DEBUG')
@click.pass_context
def cli(ctx, debug):
    ctx.debug = debug
