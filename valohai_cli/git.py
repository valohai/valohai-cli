import subprocess


def get_current_commit(directory):
    """
    (Try to) get the current commit of the Git working copy in `directory`.
    :param directory: Directory path.
    :return: Commit SHA
    :rtype: str
    """
    return subprocess.check_output(
        'git rev-parse HEAD',
        cwd=directory,
        shell=True,
    ).strip().decode()
