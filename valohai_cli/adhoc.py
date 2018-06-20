import click
import os
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from valohai_cli.api import request
from valohai_cli.messages import success, warn
from valohai_cli.packager import package_directory

def create_adhoc_commit(project):
    """
    Create an ad-hoc tarball and commit of the project directory.

    :param project: Project
    :type project: valohai_cli.models.project.Project
    :return: Commit response object from API
    :rtype: dict[str, object]
    """
    tarball = None
    try:
        click.echo('Packaging {dir}...'.format(dir=project.directory))
        tarball = package_directory(project.directory, progress=True)
        # TODO: We could check whether the commit is known already
        size = os.stat(tarball).st_size

        click.echo('Uploading {size:.2f} KiB...'.format(size=size / 1024.))
        with open(tarball, 'rb') as tarball_fp:
            upload = MultipartEncoder({'data': ('data.tgz', tarball_fp, 'application/gzip')})
            prog = click.progressbar(length=upload.len, width=0)
            prog.is_hidden = (size < 524288)  # Don't bother with the bar if the upload is small
            with prog:
                def callback(upload):
                    prog.pos = upload.bytes_read
                    prog.update(0)  # Step is 0 because we set pos above

                monitor = MultipartEncoderMonitor(upload, callback)
                resp = request(
                    'post',
                    '/api/v0/projects/{id}/import-package/'.format(id=project.id),
                    data=monitor,
                    headers={'Content-Type': monitor.content_type},
                ).json()
        success('Uploaded ad-hoc code {identifier}'.format(identifier=resp['identifier']))
    finally:
        if tarball:
            try:
                os.unlink(tarball)
            except OSError as err:  # pragma: no cover
                warn('Unable to remove temporary file: {}'.format(err))
    return resp
