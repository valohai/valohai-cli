import re
from typing import Any, Iterable, List, Optional, Union

import click

from valohai_cli.utils import force_text
from valohai_cli.utils.cli_utils import join_with_style


def match_prefix(choices: Iterable[Any], value: str, return_unique: bool = True) -> Union[List[Any], Any, None]:
    """
    Match `value` in `choices` by case-insensitive prefix matching.

    If the exact `value` is in `choices` (and `return_unique` is set),
    that exact value is returned as-is.

    :param choices: Choices to match in. May be non-string; `str()` is called on them if not.
    :param value: The value to use for matching.
    :param return_unique: If only one option was found, return it; otherwise return None.
                          If this is not true, all of the filtered choices are returned.
    :return: list, object or none; see the `return_unique` option.
    """
    if return_unique and value in choices:
        return value
    value_re = re.compile(f'^{re.escape(value)}', re.I)
    choices = [choice for choice in choices if value_re.match(force_text(choice))]
    if return_unique:
        return (choices[0] if len(choices) == 1 else None)
    return choices


def match_from_list_with_error(
    options: Iterable[str],
    input: str,
    noun: str = "object",
    param_hint: Optional[str] = None,
) -> str:
    """
    Wrap `match_prefix` and raise a pretty CLI error if no match is found, or if multiple matches are found.
    """
    if input in options:
        return input
    matching_options = match_prefix(options, input, return_unique=False)
    if not matching_options:
        styled_options = join_with_style(sorted(options), bold=True)
        raise click.BadParameter(
            f'"{input}" is not a known {noun} (try one of {styled_options})', param_hint=param_hint)
    if len(matching_options) > 1:
        styled_matches = join_with_style(sorted(matching_options), bold=True)
        styled_options = join_with_style(sorted(options), bold=True)
        raise click.BadParameter(
            f'"{input}" is ambiguous.\nIt matches {styled_matches}.\nKnown {noun} are {styled_options}.',
            param_hint=param_hint,
        )
    return str(matching_options[0])
