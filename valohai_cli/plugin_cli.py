import pkgutil
from collections import defaultdict
from importlib import import_module

import click

from valohai_cli.utils import cached_property, match_prefix


class PluginCLI(click.MultiCommand):
    aliases = {
        'new': 'create',
        'start': 'run',
    }

    def __init__(self, **kwargs):
        self._commands_module = kwargs.pop('commands_module')
        self.aliases = dict(self.aliases, **kwargs.get('aliases', {}))  # instance level copy
        super(PluginCLI, self).__init__(**kwargs)

    @cached_property
    def commands_module(self):
        if isinstance(self._commands_module, str):
            return import_module(self._commands_module)
        return self._commands_module

    @cached_property
    def command_modules(self):
        return sorted(c[1] for c in pkgutil.iter_modules(self.commands_module.__path__))

    @cached_property
    def command_to_canonical_map(self):
        command_map = dict((command, command) for command in self.command_modules)
        for alias_from, alias_to in self.aliases.items():
            if alias_to in command_map:
                command_map[alias_from] = command_map.get(alias_to, alias_to)  # resolve aliases
        return command_map

    def list_commands(self, ctx):
        return self.command_modules

    def get_command(self, ctx, name):
        command_map = self.command_to_canonical_map
        if name in command_map:
            return self._get_command(command_map[name])

        matches = match_prefix(command_map.keys(), name, return_unique=False)
        if not matches:
            return None
        if len(matches) > 1:
            ctx.fail('"{name}" matches {matches}; be more specific?'.format(
                name=name,
                matches=', '.join(click.style(match, bold=True) for match in sorted(matches))
            ))
            return
        return self._get_command(command_map[matches[0]])

    def resolve_command(self, ctx, args):
        cmd_name, cmd, rest_args = super(PluginCLI, self).resolve_command(ctx, args)
        return (cmd.name, cmd, rest_args)  # Always use the canonical name of the command

    def _get_command(self, name):
        module = import_module('%s.%s' % (self.commands_module.__name__, name))
        return getattr(module, name)


class RecursiveHelpPluginCLI(PluginCLI):

    def format_commands(self, ctx, formatter):
        rows_by_prefix = defaultdict(list)

        def add_commands(multicommand, prefix=''):
            for subcommand in multicommand.list_commands(ctx):
                cmd = multicommand.get_command(ctx, subcommand)
                assert cmd is not None
                rows_by_prefix[prefix.strip()].append((prefix + subcommand, (cmd.short_help or '')))
                if isinstance(cmd, click.MultiCommand):
                    add_commands(cmd, prefix + '%s ' % cmd.name)

        add_commands(self)
        for prefix, rows in sorted(rows_by_prefix.items()):
            title = (
                'Commands (%s ...)' % prefix
                if prefix
                else 'Commands'
            )
            with formatter.section(title):
                formatter.write_dl(rows)
