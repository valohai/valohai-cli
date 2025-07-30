from __future__ import annotations

import glob
import os
import random
import re
import string
import time
import unicodedata
import webbrowser
from collections.abc import Iterable, Iterator
from typing import Any, Callable, TypeVar

import click

ansi_escape_re = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")  # https://stackoverflow.com/a/14693789/51685
control_character_re = re.compile(r"[\x00-\x1F\x7F\x80-\x9F]")
control_characters_re = re.compile(f"{control_character_re.pattern}+")


def walk_directory_parents(dir: str) -> Iterator[str]:
    """
    Yield the passed directory and its parents' names, all the way up until filesystem root.

    :param dir: A directory path.
    :return: directories!
    """
    assert os.path.isdir(dir)
    dir = os.path.realpath(dir)
    while True:
        yield dir
        new_dir = os.path.dirname(dir)
        if dir == new_dir:  # We've reached the root!
            break
        dir = new_dir


def get_project_directory() -> str:
    dir = os.environ.get("VALOHAI_PROJECT_DIR") or os.getcwd()
    return os.path.realpath(dir)


def get_random_string(length: int = 12, keyspace: str = (string.ascii_letters + string.digits)) -> str:
    return "".join(random.choice(keyspace) for x in range(length))


def force_text(v: str | bytes, encoding: str = "UTF-8", errors: str = "strict") -> str:
    if isinstance(v, str):
        return v
    elif isinstance(v, bytes):
        return v.decode(encoding, errors)
    return str(v)


def force_bytes(v: str | int, encoding: str = "UTF-8", errors: str = "strict") -> bytes:
    if isinstance(v, bytes):
        return v
    return str(v).encode(encoding, errors)


def humanize_identifier(identifier: str) -> str:
    return re.sub("[-_]+", " ", force_text(identifier)).strip()


extension_to_interpreter: dict[str, str] = {
    ".lua": "lua",
    ".py": "python",
    ".rb": "ruby",
    ".sh": "bash",
}


def find_scripts(directory: str) -> Iterator[tuple[str, str]]:
    """
    Yield pairs of (interpreter, filename) for scripts found in `directory`.

    :param directory: Directory to look in
    :return: Pairs of interpreter and filename
    """
    for filename in glob.glob(os.path.join(directory, "*.*")):
        interpreter = extension_to_interpreter.get(os.path.splitext(filename.lower())[1])
        if interpreter:
            yield (interpreter, os.path.basename(filename))


def open_browser(object: dict[str, Any], url_name: str = "display") -> bool:
    if "urls" not in object:
        return False
    url = object["urls"][url_name]
    click.echo(f"Opening {click.style(url, bold=True)} ...")
    webbrowser.open(url)
    return True


def subset_keys(dict: dict[Any, Any], keys: Iterable[Any]) -> dict[Any, Any]:
    return {key: dict[key] for key in dict if key in keys}


def clean_log_line(line: str) -> str:
    line = force_text(line)
    line = ansi_escape_re.sub("", line)
    line = control_characters_re.sub(" ", line)
    return line.strip()


def ensure_makedirs(path: str, mode: int = 0o744) -> None:
    # http://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-python
    original_umask = os.umask(0)
    try:
        # only newly create directories get the defined mode
        if not os.path.exists(path):
            os.makedirs(path, mode)
        # ensure that the last directory has the right mode if it exists
        os.chmod(path, mode)
    finally:
        os.umask(original_umask)


def sanitize_filename(name: str, replacement: str = "-") -> str:
    # Via https://github.com/parshap/node-sanitize-filename/blob/0d21bf13be419fcde5bc3f241672bd29f7e72c63/index.js
    return re.sub(r'[\x00-\x1f\x80-\x9f/?<>\\:*|"]', replacement, name)


def sanitize_option_name(name: str) -> str:
    # In order to comply with `click.core.Option#_parse_decls`, this should
    # actually ensure `name` is a valid Python identifier (`s.isidentifier()`)
    # after dashes are replaced with underscores.
    #
    # However, what with Unicode letter characters being allowed for identifiers,
    # the rules for `.isidentifier` are, ah, arcane to say the least.
    #
    # Instead, we'll just fold everything down to ASCII with the good old
    # normalize-and-encode-and-decode dance, and then replace everything
    # non-alphanumeric into dashes to be safe.
    name = unicodedata.normalize("NFKD", str(name)).encode("ascii", errors="ignore").decode()
    return re.sub(r"[^-a-z0-9]+", "-", name, flags=re.IGNORECASE).strip("-")


# Once mypy supports using TypeVars in default arguments, we can make a more specific type for coerce.
# Mypy issue: https://github.com/python/mypy/issues/3737
def parse_environment_variable_strings(
    envvar_strings: Iterable[str],
    *,
    coerce: Callable[[str], Any] = str,
) -> dict[str, Any]:
    """
    Parse a list of environment variable strings into a dict.
    """
    environment_variables = {}
    for envstr in envvar_strings:
        key, _, value = envstr.partition("=")
        key = key.strip()
        if not key:
            continue
        environment_variables[key] = coerce(value.strip())
    return environment_variables


def compact_dict(dct: dict) -> dict:
    return {key: value for (key, value) in dct.items() if key and value}


T = TypeVar("T")


def call_with_retry(
    func: Callable[[], T],
    retries: int = 3,
    delay_range: tuple[int, int] = (1, 5),
    retry_on_exception_classes: tuple[type[Exception], ...] = (Exception,),
) -> T:
    for attempt in range(retries):
        try:
            return func()
        except retry_on_exception_classes as e:
            click.echo(f"{attempt + 1}/{retries} Retrying: {e}...")
            if attempt + 1 == retries:
                raise RuntimeError(f"Failed after {retries} attempts") from e
            time.sleep(random.uniform(*delay_range))

    raise RuntimeError("Shouldn't get here!")
