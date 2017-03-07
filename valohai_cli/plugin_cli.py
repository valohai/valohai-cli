import pkgutil
from importlib import import_module

import click

from valohai_cli.utils import cached_property, match_prefix


class PluginCLI(click.MultiCommand):
    def __init__(self, **kwargs):
        self._commands_module = kwargs.pop('commands_module')
        super(PluginCLI, self).__init__(**kwargs)

    @cached_property
    def commands_module(self):
        if isinstance(self._commands_module, str):
            return import_module(self._commands_module)
        return self._commands_module

    @cached_property
    def command_modules(self):
        return sorted(c[1] for c in pkgutil.iter_modules(self.commands_module.__path__))

    def list_commands(self, ctx):
        return self.command_modules

    def get_command(self, ctx, name):
        if name in self.command_modules:
            return self._get_command(name)

        matches = match_prefix(self.command_modules, name, return_unique=False)
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
        module = import_module('%s.%s' % (self.commands_module.__name__, name))
        return getattr(module, name)
