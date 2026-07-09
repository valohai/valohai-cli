from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import (
    Any,
    Callable,
    TypeVar,
)

import click

from valohai_cli.help_texts import EXECUTION_COUNTER_HELP

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def _default_name_formatter(option: Any) -> str:
    if isinstance(option, dict) and "name" in option:
        return str(option["name"])
    return str(option)


def prompt_from_list(
    options: Sequence[dict],
    prompt: str,
    nonlist_validator: Callable[[str], Any | None] | None = None,
    name_formatter: Callable[[dict], str] = _default_name_formatter,
) -> Any | dict:
    for i, option in enumerate(options, 1):
        number_prefix = click.style(f"[{i:3d}]", fg="cyan")
        description_suffix = (
            click.style(f'({option["description"]})', dim=True) if option.get("description") else ""
        )
        click.echo(f"{number_prefix} {name_formatter(option)} {description_suffix}")
    while True:
        answer = click.prompt(prompt)
        if answer.isdigit() and (1 <= int(answer) <= len(options)):
            return options[int(answer) - 1]
        if nonlist_validator:
            retval = nonlist_validator(answer)
            if retval:
                return retval
        for option in options:
            if answer == option["name"]:
                return option
        click.secho("Sorry, try again.")
        continue


class HelpfulArgument(click.Argument):
    def __init__(self, param_decls: list[str], help: str | None = None, **kwargs: Any) -> None:
        self.help = help
        super().__init__(param_decls, **kwargs)

    def get_help_record(self, ctx: click.Context) -> tuple[str, str] | None:  # noqa: ARG002
        if self.name and self.help:
            return (self.name, self.help)
        return None


def counter_argument(fn: FuncT) -> FuncT:
    # Extra gymnastics needed because `click.arguments` mutates the kwargs here
    arg = click.argument("counter", help=EXECUTION_COUNTER_HELP, cls=HelpfulArgument)
    return arg(fn)


def join_with_style(items: Iterable[Any], separator: str = ", ", **style_kwargs: Any) -> str:
    return separator.join(click.style(str(item), **style_kwargs) for item in items)


class PriorityHackCommand(click.Command):
    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        # Hack to allow --priority without value to work as --priority=1
        # on various versions of Click; see https://github.com/pallets/click/issues/3084
        # and other attached issues...
        try:
            priority_arg_index = args.index("--priority")
        except ValueError:
            pass
        else:
            # If it's the last argument, we can just replace it with --priority=1.
            if priority_arg_index == len(args) - 1:
                args[priority_arg_index] = "--priority=1"
            else:
                # If it's not the last argument, we need to check that the next argument is not a value for --priority.
                next_arg = args[priority_arg_index + 1]
                if next_arg.startswith("-"):
                    args[priority_arg_index] = "--priority=1"
        return super().parse_args(ctx, args)


def priority_option(fn: FuncT) -> FuncT:
    """Add a `--priority` option that also accepts a bare `--priority` (implying priority 1)."""
    option = click.option(
        "--priority",
        type=int,
        help=(
            "Priority for the job; higher values mean higher priority. "
            "May also be passed as just `--priority`, implying priority 1."
        ),
    )
    return option(fn)
