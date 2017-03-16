import subprocess

from valohai_cli.exceptions import NoGitRepo


def get_current_commit(directory):
    """
    (Try to) get the current commit of the Git working copy in `directory`.
    :param directory: Directory path.
    :return: Commit SHA
    :rtype: str
    """
    try:
        return subprocess.check_output(
            'git rev-parse HEAD',
            cwd=directory,
            shell=True,
            stderr=subprocess.STDOUT,
        ).strip().decode()
    except subprocess.CalledProcessError as cpe:
        if cpe.returncode == 128 and 'Not a git repository' in cpe.output.decode():
            raise NoGitRepo(directory)
        raise
