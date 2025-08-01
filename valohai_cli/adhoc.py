from __future__ import annotations

import os
from typing import Any

import click
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from valohai_cli.api import request
from valohai_cli.exceptions import APIError, NoCommit, NoGitRepo
from valohai_cli.git import describe_current_commit
from valohai_cli.messages import success, warn
from valohai_cli.models.project import Project
from valohai_cli.packager import package_directory
from valohai_cli.utils.file_size_format import filesizeformat
from valohai_cli.utils.hashing import get_fp_sha256


def package_adhoc_commit(
    project: Project,
    validate: bool = True,
    yaml_path: str | None = None,
    allow_git: bool = True,
) -> dict[str, Any]:
    """
    Create an ad-hoc tarball and commit of the project directory.

    :return: Commit response object from API
    """
    project.refresh_details()
    directory = project.directory
    tarball = None
    try:
        description = ""
        try:
            description = describe_current_commit(directory)
        except (NoGitRepo, NoCommit):
            pass
        except Exception as exc:
            warn(f"Unable to derive Git description: {exc}")

        if description:
            click.echo(f"Packaging {directory} ({description})...")
        else:
            click.echo(f"Packaging {directory}...")

        yaml_path = yaml_path or project.get_yaml_path()
        tarball = package_directory(
            directory=directory,
            progress=True,
            validate=validate,
            yaml_path=yaml_path,
            allow_git=allow_git,
        )
        return create_adhoc_commit_from_tarball(
            project=project,
            tarball=tarball,
            yaml_path=yaml_path,
            description=description,
        )
    finally:
        if tarball:
            try:
                os.unlink(tarball)
            except OSError as err:  # pragma: no cover
                warn(f"Unable to remove temporary file: {err}")


def create_adhoc_commit_from_tarball(
    *,
    project: Project,
    tarball: str,
    yaml_path: str | None = None,
    description: str = "",
) -> dict[str, Any]:
    """
    Using a precreated ad-hoc tarball, create or retrieve an ad-hoc commit of it on the Valohai host.

    :param project: Project
    :param tarball: Tgz tarball path, likely created by the packager
    :param yaml_path: Optional custom yaml path attached to the command.
    :param description: Optional description for the commit
    :return: Commit response object from API
    """
    yaml_path = yaml_path or project.get_yaml_path()
    commit_obj = _get_pre_existing_commit(tarball, project.id)
    if commit_obj:
        success(f"Ad-hoc code {commit_obj['identifier']} already uploaded")
    else:
        commit_obj = _upload_commit_code(
            project=project,
            tarball=tarball,
            yaml_path=yaml_path,
            description=description,
        )
    return commit_obj


def _get_pre_existing_commit(tarball: str, project_id: str) -> dict | None:
    try:
        # This is the same mechanism used by the server to
        # calculate the identifier for an ad-hoc tarball.
        with open(tarball, "rb") as tarball_fp:
            commit_identifier = f"~{get_fp_sha256(tarball_fp)}"

        # See if we have a commit with that identifier
        commit_obj: dict[str, Any] = request(
            "get",
            f"/api/v0/commits/{commit_identifier}/",
            params={"project": project_id},
        ).json()
        return commit_obj if commit_obj.get("adhoc") else None
    except APIError:
        # In the case of any API errors, let's just assume the commit doesn't exist.
        return None


def _upload_commit_code(*, project: Project, tarball: str, yaml_path: str, description: str = "") -> dict:
    size = os.stat(tarball).st_size
    click.echo(f"Uploading {filesizeformat(size)}...")
    with open(tarball, "rb") as tarball_fp:
        upload = MultipartEncoder({
            "data": ("data.tgz", tarball_fp, "application/gzip"),
            "description": description,
            "yaml_path": yaml_path,
        })
        prog = click.progressbar(length=upload.len, width=0)  # type: ignore[var-annotated]
        # Don't bother with the bar if the upload is small
        prog.is_hidden = size < 524288
        with prog:

            def callback(upload: Any) -> None:
                prog.pos = upload.bytes_read
                prog.update(0)  # Step is 0 because we set pos above

            monitor = MultipartEncoderMonitor(upload, callback)
            commit_obj: dict = request(
                "post",
                f"/api/v0/projects/{project.id}/import-package/",
                data=monitor,
                headers={"Content-Type": monitor.content_type},
            ).json()
    config_detail = f" from configuration YAML at {yaml_path}" if yaml_path else ""
    success(f"Uploaded ad-hoc code {commit_obj['identifier']}{config_detail}")
    return commit_obj
