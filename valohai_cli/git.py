import os
import subprocess

from valohai_cli.exceptions import NoGitRepo


def check_git_output(args, directory):
    try:
        return subprocess.check_output(
            args=args,
            cwd=directory,
            shell=False,
            stderr=subprocess.STDOUT,
            env=dict(os.environ, LC_ALL='C'),
        )
    except subprocess.CalledProcessError as cpe:
        if cpe.returncode == 128 and 'not a git repository' in cpe.output.decode().lower():
            raise NoGitRepo(directory)
        raise


def get_current_commit(directory):
    """
    (Try to) get the current commit of the Git working copy in `directory`.
    :param directory: Directory path.
    :return: Commit SHA
    :rtype: str
    """
    return check_git_output(['git', 'rev-parse', 'HEAD'], directory).strip().decode()


def get_file_at_commit(directory, commit, path):
    """
    Get the contents of repository `path` at commit `commit` given the
    Git working directory `directory`.

    :param directory: Git working directory.
    :param commit: Commit ID
    :param path: In-repository path
    :return: File contents as bytes
    :rtype: bytes
    """
    args = ['git', 'show', '{}:{}'.format(commit, path)]
    return check_git_output(args, directory)


def expand_commit_id(directory, commit):
    """
    Expand the possibly abbreviated (or otherwise referred to, i.e. "HEAD")
    commit ID, and verify it exists.

    :param directory: Git working directory
    :param commit: Commit ID
    :return: Expanded commit ID.
    """
    return check_git_output(['git', 'rev-parse', '--verify', commit], directory).decode().strip()
