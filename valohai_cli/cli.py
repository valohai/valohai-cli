import logging

import click

from valohai_cli.plugin_cli import RecursiveHelpPluginCLI
from valohai_cli.table import TABLE_FORMATS, TABLE_FORMAT_META_KEY


@click.command(cls=RecursiveHelpPluginCLI, commands_module='valohai_cli.commands')
@click.option('--debug/--no-debug', default=False, envvar='VALOHAI_DEBUG')
@click.option('--table-format', type=click.Choice(TABLE_FORMATS), default='human')
@click.pass_context
def cli(ctx, debug, table_format):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    ctx.debug = debug
    ctx.meta[TABLE_FORMAT_META_KEY] = table_format
