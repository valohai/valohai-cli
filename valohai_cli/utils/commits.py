from typing import Optional, Union

import click

from valohai_cli import git as git
from valohai_cli.adhoc import package_adhoc_commit
from valohai_cli.exceptions import NoGitRepo
from valohai_cli.messages import warn
from valohai_cli.models.project import Project
from valohai_cli.models.remote_project import RemoteProject


def create_or_resolve_commit(
    project: Union[RemoteProject, Project],
    *,
    commit: Optional[str],
    adhoc: bool,
    validate_adhoc_commit: bool = True,
) -> str:
    if adhoc:
        if project.is_remote:
            raise click.UsageError('--adhoc can not be used with remote projects.')
        if commit:
            raise click.UsageError('--commit and --adhoc are mutually exclusive.')
        commit = str(package_adhoc_commit(project, validate=validate_adhoc_commit)['identifier'])

    commit = commit or get_git_commit(project)
    return resolve_commit(commit, project)


def get_git_commit(project: Project) -> Optional[str]:
    try:
        return git.get_current_commit(project.directory)
    except NoGitRepo:
        warn(
            'The directory is not a Git repository. \n'
            'Would you like to just run using the latest commit known by Valohai?'
        )
        if not click.confirm('Use latest commit?', default=True):
            raise click.Abort()
        return None


def resolve_commit(commit_identifier: Optional[str], project: Project) -> str:
    if commit_identifier and commit_identifier.startswith('~'):
        # Assume ad-hoc commits are qualified already
        return commit_identifier

    try:
        commit_obj = project.resolve_commit(commit_identifier=commit_identifier)
    except KeyError:
        warn(f'Commit {commit_identifier} is not known for the project. Have you pushed it?')
        raise click.Abort()
    except IndexError:
        warn('No commits are known for the project.')
        raise click.Abort()

    resolved_commit_identifier: str = commit_obj['identifier']
    if not commit_identifier:
        click.echo(f'Resolved to commit {resolved_commit_identifier}', err=True)

    return resolved_commit_identifier
