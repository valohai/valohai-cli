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
        if len(matches) == 1:
            match = command_map[matches[0]]
            return self._get_command(match)

        if ' ' not in name:
            # Try word suffix matching if possible.
            # That is, if the user attempts `vh link` but we know about `vh proj link`, do that.
            command_map = {' '.join(trail): cmd for (trail, cmd) in self._get_all_commands(ctx)}
            s_matches = [key for key in command_map.keys() if ' ' in key and key.endswith(' ' + name)]
            if len(s_matches) == 1:
                match = s_matches[0]
                click.echo('(Resolved {name} to {match}.)'.format(
                    name=click.style(name, bold=True),
                    match=click.style(match, bold=True),
                ), err=True)
                return command_map[match]

        if len(matches) > 1:
            ctx.fail('"{name}" matches {matches}; be more specific?'.format(
                name=name,
                matches=', '.join(click.style(match, bold=True) for match in sorted(matches))
            ))
            return None

    def resolve_command(self, ctx, args):
        cmd_name, cmd, rest_args = super(PluginCLI, self).resolve_command(ctx, args)
        return (cmd.name, cmd, rest_args)  # Always use the canonical name of the command

    def _get_command(self, name):
        module = import_module('%s.%s' % (self.commands_module.__name__, name))
        return getattr(module, name)

    def _get_all_commands(self, ctx):
        def walk_commands(multicommand, name_trail=()):
            for subcommand in multicommand.list_commands(ctx):
                cmd = multicommand.get_command(ctx, subcommand)
                assert cmd is not None
                new_name_trail = name_trail + (cmd.name,)
                yield (new_name_trail, cmd)
                if isinstance(cmd, click.MultiCommand):
                    for o in walk_commands(cmd, new_name_trail):
                        yield o

        for o in walk_commands(self):
            yield o


class RecursiveHelpPluginCLI(PluginCLI):

    def format_commands(self, ctx, formatter):
        rows_by_prefix = defaultdict(list)
        for trail, command in self._get_all_commands(ctx):
            prefix = (' '.join(trail[:1]) if len(trail) > 1 else '')
            help = (command.short_help or command.help or '').partition('\n')[0]
            rows_by_prefix[prefix.strip()].append((' '.join(trail).strip(), help))

        for prefix, rows in sorted(rows_by_prefix.items()):
            title = (
                'Commands (%s ...)' % prefix
                if prefix
                else 'Commands'
            )
            with formatter.section(title):
                formatter.write_dl(rows)
