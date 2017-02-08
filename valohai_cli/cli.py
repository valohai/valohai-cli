import pkgutil
from importlib import import_module

import click

from . import commands as commands_module
command_modules = sorted(c[1] for c in pkgutil.iter_modules(commands_module.__path__))


class PluginCLI(click.MultiCommand):
    def list_commands(self, ctx):
        return command_modules

    def get_command(self, ctx, name):
        if name in command_modules:
            module = import_module('%s.%s' % (commands_module.__name__, name))
            return getattr(module, name)


@click.command(cls=PluginCLI)
@click.option('--debug/--no-debug', default=False, envvar='VALOHAI_DEBUG')
@click.pass_context
def cli(ctx, debug):
    ctx.debug = debug
