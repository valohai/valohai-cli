from __future__ import annotations

import re
from collections.abc import Iterable
from re import Pattern
from typing import Any, Callable, Union

StringOrPattern = Union[str, Pattern]


def _match_string(s: str | None, pattern: StringOrPattern) -> bool:
    if s is None:
        return False
    if isinstance(pattern, re.Pattern):
        return bool(pattern.match(s))
    return s == pattern


def match_error(
    response_data: dict,
    *,
    code: StringOrPattern | None = None,
    message: StringOrPattern | None = None,
    matcher: Callable | None = None,
) -> dict | None:
    if code and not _match_string(response_data.get("code"), code):
        return None
    if message and not _match_string(response_data.get("message"), message):
        return None
    if matcher and not matcher(message):
        return None
    return response_data


def find_error(
    response_data: Any,
    *,
    code: StringOrPattern | None = None,
    message: StringOrPattern | None = None,
    matcher: Callable | None = None,
) -> Any | None:
    if response_data is None:
        # Error not found in response
        return False

    iterable: Iterable[Any] | None = None
    if isinstance(response_data, str):
        return match_error(
            {"message": response_data, "code": None},
            code=code,
            message=message,
            matcher=matcher,
        )

    if isinstance(response_data, dict):
        if "code" in response_data and "message" in response_data:  # Smells like the actual error object
            return match_error(response_data, code=code, message=message, matcher=matcher)
        iterable = response_data.values()
    elif isinstance(response_data, list):
        iterable = response_data

    if iterable is not None:
        for value in iterable:
            rv = find_error(value, code=code, message=message, matcher=matcher)
            if rv:
                return rv
    else:
        raise TypeError(f"Can not find_error in {response_data!r}")
    return None
