import glob
import os
import random
import re
import string
import webbrowser

import click
import six


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
    if isinstance(v, six.text_type):
        return v
    elif isinstance(v, six.binary_type):
        return v.decode(encoding, errors)
    return six.text_type(v)


def force_bytes(v, encoding='UTF-8', errors='strict'):
    if isinstance(v, six.binary_type):
        return v
    return six.text_type(v).encode(encoding, errors)


def match_prefix(choices, value, return_unique=True):
    """
    Match `value` in `choices` by case-insensitive prefix matching.

    :param choices: Choices to match in. May be non-string; `str()` is called on them if not.
    :param value: The value to use for matching.
    :param return_unique: If only one option was found, return it; otherwise return None.
                          If this is not true, all of the filtered choices are returned.
    :return: list, object or none; see the `return_unique` option.
    :rtype: list[object]|object|None
    """
    value_re = re.compile('^' + re.escape(value), re.I)
    choices = [choice for choice in choices if value_re.match(force_text(choice))]
    if return_unique:
        return (choices[0] if len(choices) == 1 else None)
    return choices


def humanize_identifier(identifier):
    return re.sub('[-_]+', ' ', force_text(identifier)).strip()


class cached_property(object):
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
