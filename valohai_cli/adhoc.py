import os

import click
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from valohai_cli.api import request
from valohai_cli.exceptions import APIError, NoCommit, NoGitRepo
from valohai_cli.git import describe_current_commit
from valohai_cli.messages import success, warn
from valohai_cli.packager import package_directory
from valohai_cli.utils.file_size_format import filesizeformat
from valohai_cli.utils.hashing import get_fp_sha256


def package_adhoc_commit(project, validate=True):
    """
    Create an ad-hoc tarball and commit of the project directory.

    :param project: Project
    :type project: valohai_cli.models.project.Project
    :return: Commit response object from API
    :rtype: dict[str, object]
    """
    tarball = None
    try:
        description = ''
        try:
            description = describe_current_commit(project.directory)
        except (NoGitRepo, NoCommit):
            pass
        except Exception as exc:
            warn('Unable to derive Git description: %s' % exc)

        if description:
            click.echo(f'Packaging {project.directory} ({description})...')
        else:
            click.echo(f'Packaging {project.directory}...')
        tarball = package_directory(project.directory, progress=True, validate=validate)
        return create_adhoc_commit_from_tarball(project, tarball, description)
    finally:
        if tarball:
            try:
                os.unlink(tarball)
            except OSError as err:  # pragma: no cover
                warn(f'Unable to remove temporary file: {err}')


# Compatibility alias.
# TODO: Remove in 2020.
create_adhoc_commit = package_adhoc_commit


def create_adhoc_commit_from_tarball(project, tarball, description=''):
    """
    Using a precreated ad-hoc tarball, create or retrieve an ad-hoc commit of it on the Valohai host.

    :param project: Project
    :type project: valohai_cli.models.project.Project
    :param tarball: Tgz tarball path, likely created by the packager
    :type tarball: str
    :param description: Optional description for the commit
    :type description: str
    :return: Commit response object from API
    :rtype: dict[str, object]
    """
    commit_obj = _get_pre_existing_commit(tarball)
    if commit_obj:
        success('Ad-hoc code {identifier} already uploaded'.format(identifier=commit_obj['identifier']))
    else:
        commit_obj = _upload_commit_code(project, tarball, description)
    return commit_obj


def _get_pre_existing_commit(tarball):
    try:
        # This is the same mechanism used by the server to
        # calculate the identifier for an ad-hoc tarball.
        with open(tarball, 'rb') as tarball_fp:
            commit_identifier = '~{hash}'.format(hash=get_fp_sha256(tarball_fp))

        # See if we have a commit with that identifier
        commit_obj = request('get', f'/api/v0/commits/{commit_identifier}/').json()
        return (commit_obj if commit_obj.get('adhoc') else None)
    except APIError:
        # In the case of any API errors, let's just assume the commit doesn't exist.
        return None


def _upload_commit_code(project, tarball, description=''):
    size = os.stat(tarball).st_size
    click.echo('Uploading {size}...'.format(size=filesizeformat(size)))
    with open(tarball, 'rb') as tarball_fp:
        upload = MultipartEncoder({
            'data': ('data.tgz', tarball_fp, 'application/gzip'),
            'description': description,
        })
        prog = click.progressbar(length=upload.len, width=0)
        prog.is_hidden = (size < 524288)  # Don't bother with the bar if the upload is small
        with prog:
            def callback(upload):
                prog.pos = upload.bytes_read
                prog.update(0)  # Step is 0 because we set pos above

            monitor = MultipartEncoderMonitor(upload, callback)
            commit_obj = request(
                'post',
                f'/api/v0/projects/{project.id}/import-package/',
                data=monitor,
                headers={'Content-Type': monitor.content_type},
            ).json()
    success('Uploaded ad-hoc code {identifier}'.format(identifier=commit_obj['identifier']))
    return commit_obj
