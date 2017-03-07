import pkgutil
from importlib import import_module

import click

from . import commands as commands_module
from .utils import match_prefix

command_modules = sorted(c[1] for c in pkgutil.iter_modules(commands_module.__path__))


class PluginCLI(click.MultiCommand):
    def list_commands(self, ctx):
        return command_modules

    def get_command(self, ctx, name):
        if name in command_modules:
            return self._get_command(name)

        matches = match_prefix(command_modules, name, return_unique=False)
        if not matches:
            return None
        if len(matches) > 1:
            ctx.fail('"{name}" matches {matches}; be more specific?'.format(
                name=name,
                matches=', '.join(click.style(match, bold=True) for match in sorted(matches))
            ))
            return
        return self._get_command(matches[0])

    def resolve_command(self, ctx, args):
        cmd_name, cmd, rest_args = super().resolve_command(ctx, args)
        return (cmd.name, cmd, rest_args)  # Always use the canonical name of the command

    def _get_command(self, name):
        module = import_module('%s.%s' % (commands_module.__name__, name))
        return getattr(module, name)


@click.command(cls=PluginCLI)
@click.option('--debug/--no-debug', default=False, envvar='VALOHAI_DEBUG')
@click.pass_context
def cli(ctx, debug):
    ctx.debug = debug
