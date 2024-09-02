from typing import List, Optional, Union

import click
from click import get_current_context

from valohai_cli import git as git
from valohai_cli.adhoc import package_adhoc_commit
from valohai_cli.commands.project.fetch import fetch
from valohai_cli.ctx import get_project
from valohai_cli.exceptions import NoGitRepo
from valohai_cli.messages import warn
from valohai_cli.models.project import Project
from valohai_cli.models.remote_project import RemoteProject


def create_or_resolve_commit(
    project: Union[RemoteProject, Project],
    *,
    commit: Optional[str],
    yaml_path: Optional[str],
    adhoc: bool,
    validate_adhoc_commit: bool = True,
    allow_git_packaging: bool = True,
) -> str:
    if adhoc:
        if project.is_remote:
            raise click.UsageError("--adhoc can not be used with remote projects.")
        if commit:
            raise click.UsageError("--commit and --adhoc are mutually exclusive.")
        commit = str(
            package_adhoc_commit(
                project,
                validate=validate_adhoc_commit,
                yaml_path=yaml_path,
                allow_git=allow_git_packaging,
            )["identifier"],
        )
    elif yaml_path:
        raise click.UsageError("--yaml can only be used with --adhoc.")

    commit = commit or get_git_commit(project)
    return resolve_commit(commit, project)


def get_git_commit(project: Project) -> Optional[str]:
    try:
        return git.get_current_commit(project.directory)
    except NoGitRepo:
        warn(
            "The directory is not a Git repository. \n"
            "Would you like to just run using the latest commit known by Valohai?",
        )
        if not click.confirm("Use latest commit?", default=True):
            raise click.Abort()
        return None


def resolve_commit(commit_identifier: Optional[str], project: Project) -> str:
    matching_commits = []
    if commit_identifier and commit_identifier.startswith("~"):
        # Assume ad-hoc commits are qualified already
        return commit_identifier

    try:
        matching_commits = project.resolve_commits(commit_identifier=commit_identifier)
    except KeyError:
        warn(f"Commit {commit_identifier} is not known for the project")
        if click.confirm("Would you like to fetch new commits?", default=True):
            matching_commits = fetch_latest_commits(commit_identifier)
    except IndexError:
        warn("No commits are known for the project.")

    if not matching_commits:
        raise click.Abort()

    commit_obj = matching_commits[0]
    resolved_commit_identifier: str = commit_obj["identifier"]
    if len(matching_commits) > 1:
        ambiguous_str = ", ".join([c["identifier"] for c in matching_commits[1:]])
        click.echo(
            f"Resolved to commit {resolved_commit_identifier}, which is ambiguous with {ambiguous_str}",
            err=True,
        )
    elif not commit_identifier:
        click.echo(f"Resolved to commit {resolved_commit_identifier}", err=True)

    return resolved_commit_identifier


def fetch_latest_commits(commit_identifier: Optional[str]) -> List[dict]:
    ctx = get_current_context(silent=True)
    ctx.invoke(fetch)
    project = get_project(require=True)
    return project.resolve_commits(commit_identifier=commit_identifier)
