import glob
import os
import random
import re
import string
import unicodedata
import webbrowser

import click

ansi_escape_re = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')  # https://stackoverflow.com/a/14693789/51685
control_character_re = re.compile(r'[\x00-\x1F\x7F\x80-\x9F]')
control_characters_re = re.compile(control_character_re.pattern + '+')


def walk_directory_parents(dir):
    """
    Yield the passed directory and its parents' names, all the way up until filesystem root.

    :param dir: A directory path.
    :return: directories!
    :rtype: Iterable[str]
    """
    assert os.path.isdir(dir)
    dir = os.path.realpath(dir)
    while True:
        yield dir
        new_dir = os.path.dirname(dir)
        if dir == new_dir:  # We've reached the root!
            break
        dir = new_dir


def get_project_directory():
    dir = os.environ.get('VALOHAI_PROJECT_DIR') or os.getcwd()
    return os.path.realpath(dir)


def get_random_string(length=12, keyspace=(string.ascii_letters + string.digits)):
    return ''.join(random.choice(keyspace) for x in range(length))


def force_text(v, encoding='UTF-8', errors='strict'):
    if isinstance(v, str):
        return v
    elif isinstance(v, bytes):
        return v.decode(encoding, errors)
    return str(v)


def force_bytes(v, encoding='UTF-8', errors='strict'):
    if isinstance(v, bytes):
        return v
    return str(v).encode(encoding, errors)


def match_prefix(choices, value, return_unique=True):
    """
    Match `value` in `choices` by case-insensitive prefix matching.

    If the exact `value` is in `choices` (and `return_unique` is set),
    that exact value is returned as-is.

    :param choices: Choices to match in. May be non-string; `str()` is called on them if not.
    :param value: The value to use for matching.
    :param return_unique: If only one option was found, return it; otherwise return None.
                          If this is not true, all of the filtered choices are returned.
    :return: list, object or none; see the `return_unique` option.
    :rtype: list[object]|object|None
    """
    if return_unique and value in choices:
        return value
    value_re = re.compile('^' + re.escape(value), re.I)
    choices = [choice for choice in choices if value_re.match(force_text(choice))]
    if return_unique:
        return (choices[0] if len(choices) == 1 else None)
    return choices


def humanize_identifier(identifier):
    return re.sub('[-_]+', ' ', force_text(identifier)).strip()


class cached_property:
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    Source: https://github.com/pydanny/cached-property/blob/d4d48d2b3415c0d8f60936284109729dcbd406e6/cached_property.py
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


extension_to_interpreter = {
    '.lua': 'lua',
    '.py': 'python',
    '.rb': 'ruby',
    '.sh': 'bash',
}


def find_scripts(directory):
    """
    Yield pairs of (interpreter, filename) for scripts found in `directory`.

    :param directory: Directory to look in
    :return: Pairs of interpreter and filename
    :rtype: Iterable[tuple[str, str]]
    """
    for filename in glob.glob(os.path.join(directory, '*.*')):
        interpreter = extension_to_interpreter.get(os.path.splitext(filename.lower())[1])
        if interpreter:
            yield (interpreter, os.path.basename(filename))


def open_browser(object, url_name='display'):
    if 'urls' not in object:
        return False
    url = object['urls'][url_name]
    click.echo('Opening {} ...'.format(click.style(url, bold=True)))
    webbrowser.open(url)
    return True


def subset_keys(dict, keys):
    return {key: dict[key] for key in dict if key in keys}


def clean_log_line(line):
    line = force_text(line)
    line = ansi_escape_re.sub('', line)
    line = control_characters_re.sub(' ', line)
    return line.strip()


def ensure_makedirs(path, mode=0o744):
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


def sanitize_filename(name, replacement='-'):
    # Via https://github.com/parshap/node-sanitize-filename/blob/0d21bf13be419fcde5bc3f241672bd29f7e72c63/index.js
    return re.sub(r'[\x00-\x1f\x80-\x9f/?<>\\:*|"]', replacement, name)


def sanitize_option_name(name):
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
    name = unicodedata.normalize('NFKD', str(name)).encode('ascii', errors='ignore').decode()
    return re.sub(r'[^-a-z0-9]+', '-', name, flags=re.IGNORECASE).strip('-')


def parse_environment_variable_strings(envvar_strings):
    """
    Parse a list of environment variable strings into a dict.
    """
    environment_variables = {}
    for string in envvar_strings:
        key, _, value = string.partition('=')
        key = key.strip()
        if not key:
            continue
        environment_variables[key] = value.strip()
    return environment_variables


def compact_dict(dct: dict) -> dict:
    return {key: value for (key, value) in dct.items() if key and value}
