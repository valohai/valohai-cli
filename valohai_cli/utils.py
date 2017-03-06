import os
import random
import re
import string


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
