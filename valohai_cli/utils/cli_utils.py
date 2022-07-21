from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple, TypeVar, Union

import click

from valohai_cli.help_texts import EXECUTION_COUNTER_HELP

FuncT = TypeVar('FuncT', bound=Callable[..., Any])


def _default_name_formatter(option: Any) -> str:
    if isinstance(option, dict) and 'name' in option:
        return str(option['name'])
    return str(option)


def prompt_from_list(
    options: Sequence[dict],
    prompt: str,
    nonlist_validator: Optional[Callable[[str], Optional[Any]]] = None,
    name_formatter: Callable[[dict], str] = _default_name_formatter,
) -> Union[Any, dict]:
    for i, option in enumerate(options, 1):
        number_prefix = click.style(f'[{i:3d}]', fg='cyan')
        description_suffix = (click.style(f'({option["description"]})', dim=True) if option.get('description') else '')
        click.echo(f'{number_prefix} {name_formatter(option)} {description_suffix}')
    while True:
        answer = click.prompt(prompt)
        if answer.isdigit() and (1 <= int(answer) <= len(options)):
            return options[int(answer) - 1]
        if nonlist_validator:
            retval = nonlist_validator(answer)
            if retval:
                return retval
        for option in options:
            if answer == option['name']:
                return option
        click.secho('Sorry, try again.')
        continue


class HelpfulArgument(click.Argument):
    def __init__(self, param_decls: List[str], help: Optional[str] = None, **kwargs: Any) -> None:
        self.help = help
        super().__init__(param_decls, **kwargs)

    def get_help_record(self, ctx: click.Context) -> Optional[Tuple[str, str]]:  # noqa: U100
        if self.name and self.help:
            return (self.name, self.help)
        return None


def counter_argument(fn: FuncT) -> FuncT:
    # Extra gymnastics needed because `click.arguments` mutates the kwargs here
    arg = click.argument('counter', help=EXECUTION_COUNTER_HELP, cls=HelpfulArgument)
    return arg(fn)


def join_with_style(items: Iterable[Any], separator: str = ', ', **style_kwargs: Any) -> str:
    return separator.join(click.style(str(item), **style_kwargs) for item in items)
