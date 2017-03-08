import click

from valohai_cli.plugin_cli import RecursiveHelpPluginCLI


@click.command(cls=RecursiveHelpPluginCLI, commands_module='valohai_cli.commands')
@click.option('--debug/--no-debug', default=False, envvar='VALOHAI_DEBUG')
@click.pass_context
def cli(ctx, debug):
    ctx.debug = debug
