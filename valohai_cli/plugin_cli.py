import os
import pkgutil
from collections import defaultdict
from importlib import import_module
from types import ModuleType
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import click
from click.core import Command, Context
from click.formatting import HelpFormatter

from valohai_cli.consts import json_help_envvar
from valohai_cli.utils.cli_utils import join_with_style
from valohai_cli.utils.matching import match_prefix


class PluginCLI(click.MultiCommand):
    aliases = {
        'new': 'create',
        'start': 'run',
    }

    def __init__(self, **kwargs: Any) -> None:
        self._commands_module = kwargs.pop('commands_module')
        self._command_modules: List[str] = []
        self._command_to_canonical_map: Dict[str, str] = {}
        self.aliases = dict(self.aliases, **kwargs.get('aliases', {}))  # instance level copy
        super().__init__(**kwargs)

    @property
    def commands_module(self) -> ModuleType:
        if isinstance(self._commands_module, str):
            self._commands_module = import_module(self._commands_module)
        return self._commands_module  # type: ignore

    @property
    def command_modules(self) -> List[str]:
        if not self._command_modules:
            mod_path = self.commands_module.__path__
            self._command_modules = sorted(c[1] for c in pkgutil.iter_modules(mod_path))
        return self._command_modules

    @property
    def command_to_canonical_map(self) -> Dict[str, str]:
        if not self._command_to_canonical_map:
            command_map = {command: command for command in self.command_modules}
            for alias_from, alias_to in self.aliases.items():
                if alias_to in command_map:
                    command_map[alias_from] = command_map.get(alias_to, alias_to)  # resolve aliases
            self._command_to_canonical_map = command_map
        return self._command_to_canonical_map

    def list_commands(self, ctx: Context) -> List[str]:  # noqa: ARG002
        return self.command_modules

    def get_command(self, ctx: Context, name: str) -> Optional[Union[Command, 'PluginCLI']]:
        # Dashes aren't valid in Python identifiers, so let's just replace them here.
        name = name.replace('-', '_')

        command_map: Dict[str, str] = self.command_to_canonical_map
        if name in command_map:
            return self._get_command(command_map[name])

        matches = match_prefix(command_map.keys(), name, return_unique=False)
        if matches is None:
            matches = []
        if len(matches) == 1:
            match = command_map[matches[0]]
            return self._get_command(match)

        if ' ' not in name:
            cmd = self._try_suffix_match(ctx, name)
            if cmd:
                return cmd

        if len(matches) > 1:
            ctx.fail(f'"{name}" matches {join_with_style(sorted(matches), bold=True)}; be more specific?')
        return None

    def _try_suffix_match(self, ctx: Context, name: str) -> Optional[Command]:
        # Try word suffix matching if possible.
        # That is, if the user attempts `vh link` but we know about `vh proj link`, do that.
        command_map: Dict[str, Command] = {
            ' '.join(trail): cmd
            for (trail, cmd)
            in self._get_all_commands(ctx)
        }
        s_matches = [key for key in command_map if ' ' in key and key.endswith(f' {name}')]
        if len(s_matches) == 1:
            match = s_matches[0]
            click.echo(f'(Resolved {click.style(name, bold=True)} to {click.style(match, bold=True)}.)', err=True)
            return command_map[match]
        return None

    def resolve_command(self, ctx: Context, args: List[str]) -> Tuple[Optional[str], Optional[Command], List[str]]:
        cmd_name, cmd, rest_args = super().resolve_command(ctx, args)
        return (
            getattr(cmd, "name", cmd_name),  # Always use the canonical name of the command
            cmd,
            rest_args,
        )

    def _get_command(self, name: str) -> Command:
        module = import_module(f'{self.commands_module.__name__}.{name}')
        obj = getattr(module, name)
        assert isinstance(obj, Command)
        return obj

    def _get_all_commands(self, ctx: Context) -> Iterable[Tuple[Tuple[str, ...], Command]]:
        yield from walk_commands(ctx, self)


def walk_commands(
    ctx: click.Context,
    multicommand: click.MultiCommand,
    name_trail: Tuple[str, ...] = (),
) -> Iterable[Tuple[Tuple[str, ...], Command]]:
    for subcommand in multicommand.list_commands(ctx):
        cmd = multicommand.get_command(ctx, subcommand)
        if not (cmd and cmd.name):
            continue
        new_name_trail = name_trail + (cmd.name,)
        yield (new_name_trail, cmd)
        if isinstance(cmd, click.MultiCommand):
            yield from walk_commands(ctx, cmd, new_name_trail)


class RecursiveHelpPluginCLI(PluginCLI):

    def get_help(self, ctx: Context) -> str:
        if os.environ.get(json_help_envvar):
            # Dump JSON help. The format of this is not guaranteed to be stable,
            # as (as you can see) it's currently directly provided by Click
            # (see https://github.com/pallets/click/pull/1623).
            import json
            return json.dumps(ctx.to_info_dict())

        return super().get_help(ctx)

    def format_commands(self, ctx: Context, formatter: HelpFormatter) -> None:
        rows_by_prefix = defaultdict(list)
        for trail, command in self._get_all_commands(ctx):
            prefix = (' '.join(trail[:1]) if len(trail) > 1 else '')
            help = (command.short_help or command.help or '').partition('\n')[0]
            rows_by_prefix[prefix.strip()].append((' '.join(trail).strip(), help))

        for prefix, rows in sorted(rows_by_prefix.items()):
            title = (
                f'Commands ({prefix} ...)'
                if prefix
                else 'Commands'
            )
            with formatter.section(title):
                formatter.write_dl(rows)
