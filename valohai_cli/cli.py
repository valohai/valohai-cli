import logging
import platform
import sys

import click

from valohai_cli.consts import default_app_host
from valohai_cli.messages import warn
from valohai_cli.override import configure_token_login
from valohai_cli.plugin_cli import RecursiveHelpPluginCLI
from valohai_cli.settings import settings
from valohai_cli.table import TABLE_FORMATS


@click.command(cls=RecursiveHelpPluginCLI, commands_module='valohai_cli.commands')
@click.option('--debug/--no-debug', default=False, envvar='VALOHAI_DEBUG')
@click.option('--table-format', type=click.Choice(TABLE_FORMATS), default='human', envvar='VALOHAI_TABLE_FORMAT')
@click.option('--valohai-host', envvar='VALOHAI_HOST', metavar='URL', help='Override the Valohai API host (default %s)' % default_app_host, show_envvar=True)
@click.option('--valohai-token', envvar='VALOHAI_TOKEN', metavar='SECRET', help='Use this Valohai authentication token', show_envvar=True)
@click.pass_context
def cli(ctx, debug, table_format, valohai_host, valohai_token):
    """
    :type ctx: click.Context
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    ctx.debug = debug
    settings.table_format = table_format
    if valohai_host:
        settings.overrides['host'] = valohai_host
    if valohai_token:
        configure_token_login(host=valohai_host, token=valohai_token)

    if platform.python_implementation() in ('CPython', 'PyPy') and sys.version_info[:2] < (3, 5):
        warn(
            'A future version of the tool will drop support Python versions older than 3.5. '
            'You are currently using Python %s. Please upgrade!' % platform.python_version()
        )
