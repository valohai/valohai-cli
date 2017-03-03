import os


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
