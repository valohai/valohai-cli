from __future__ import print_function
import os
import subprocess
import sys
import time

import click

from valohai_cli.ctx import get_project
from valohai_cli.git import expand_commit_id
from valohai_cli.messages import success
from valohai_cli.tui import get_spinner_character
from valohai_cli.utils import ensure_makedirs, format_size, sanitize_filename

MINIMUM_VALOHAI_LOCAL_RUN_VERSION = '0.2.1'


def print_parcel_progress(text):
    click.secho('::: %s' % text, bold=True, fg='cyan')


@click.command()
@click.option('-d', '--destination', type=click.Path(file_okay=False, dir_okay=True), required=False)
@click.option('-c', '--commit', help='Commit to read required Docker image IDs from')
@click.option(
    '--code',
    type=click.Choice(['bundle', 'archive', 'tarball', 'none']),
    default='bundle',
    help='Package code as a full Git bundle, an archive of Git HEAD, a tarball of the directory or not at all?',
)
@click.option('--docker-images/--no-docker-images', default=True, help='Package Docker images?')
@click.option('--valohai-local-run/--no-valohai-local-run', default=True, help='Download valohai-local-run + deps?')
def parcel(destination, commit, code, valohai_local_run, docker_images):
    project = get_project(require=True)

    if not destination:
        destination = '{}-parcel-{}'.format(
            project.name,
            time.strftime('%Y%m%d-%H%M%S'),
        )

    click.echo('Packing {} to directory {}'.format(
        click.style(project.name, bold=True, fg='blue'),
        click.style(destination, bold=True, fg='green'),
    ))

    ensure_makedirs(destination)

    extra_docker_images = []

    if code in ('bundle', 'archive', 'tarball'):
        export_code(project, destination, mode=code)

    if valohai_local_run:
        export_valohai_local_run(project, destination)

    if docker_images:
        export_docker_images(project, destination, commit, extra_docker_images)

    success('Parcel {} created!'.format(destination))


def export_valohai_local_run(project, destination):
    print_parcel_progress('Downloading valohai-local-run and dependencies')
    destination = os.path.join(destination, 'python-archives')
    subprocess.check_call(
        [
            'pip',
            '--disable-pip-version-check',
            'download',
            '--dest', destination,
            'valohai-local-run>=' + MINIMUM_VALOHAI_LOCAL_RUN_VERSION,
        ],
    )


def export_code(project, destination, mode):
    if mode == 'bundle':
        print_parcel_progress('Creating Git repository bundle')
        subprocess.check_call(
            ['git', 'bundle', 'create', os.path.join(destination, 'git-repo.bundle'), '--all'],
            cwd=project.directory,
        )
    elif mode == 'archive':
        print_parcel_progress('Creating Git single-revision archive')
        subprocess.check_call(
            ['git', 'archive', '--format', 'tar', 'HEAD', '-o', os.path.join(destination, 'git-commit.tar')],
            cwd=project.directory,
        )
    elif mode == 'tarball':
        print_parcel_progress('Creating full directory tarball')
        subprocess.check_call(
            [
                'tar',
                'cvf',
                os.path.join(destination, 'code.tar'),
                '--exclude=.git',
                '--exclude=%s' % os.path.basename(destination),  # In case we're being run in the same dir
                '.',  # Correct directory taken care of with cwd
            ],
            cwd=project.directory,
        )
    else:  # pragma: no cover
        raise NotImplementedError('...')


def get_docker_image_size(image):
    """
    Try to get the size of the given Docker image in bytes.
    :param image: The image name.
    :return: Number of bytes, or None if not available.
    :rtype: int|None
    """
    try:
        size = subprocess.check_output(
            ['docker', 'images', "--format={{.Size}}", image],
        ).strip().decode()
    except subprocess.CalledProcessError:  # Something went wrong, doesn't matter what.
        return None
    # No matter what, the Docker CLI API always outputs sizes
    # in a human-readable form, so we'll try and parse that...
    for suffix, multiplier in (('GB', 1e9), ('MB', 1e6), ('kB', 1e3), ('B', 1)):
        if size.endswith(suffix):
            return int(float(size[:-len(suffix)]) * multiplier)
    return None


def export_docker_images(project, destination, commit, extra_docker_images=()):
    commit = expand_commit_id(project.directory, commit=(commit or 'HEAD'))
    docker_images = set(step.image for step in project.get_config(commit).steps.values())
    docker_images |= set(extra_docker_images)
    for i, image in enumerate(docker_images, 1):
        output_path = os.path.join(destination, sanitize_filename('docker-{}.tar'.format(image)))
        if image not in extra_docker_images:
            print_parcel_progress('::: Pulling image {}/{} ({})'.format(
                i,
                len(docker_images),
                image,
            ))
            subprocess.check_call(['docker', 'pull', image])
        print_parcel_progress('::: Exporting image {}/{} ({})'.format(
            i,
            len(docker_images),
            image,
        ))
        export_docker_image(image, output_path)


def export_docker_image(image, output_path):
    """
    Export the Docker image `image` to the tar file `output_path`,
    with visual progress.

    :param image: Image specifier
    :param output_path: Output pathname
    """
    image_size = get_docker_image_size(image)
    proc = subprocess.Popen(['docker', 'save', image], bufsize=-1, stdout=subprocess.PIPE)
    with open(output_path, 'wb') as outfp:
        if sys.stdout.isatty():
            print('Initializing export...', end='\r')
        while proc.poll() is None:
            chunk = proc.stdout.read(1048576)
            if not chunk:
                break
            outfp.write(chunk)
            if sys.stdout.isatty():
                width = click.get_terminal_size()[0]
                status_text = '{} {}: {} / {}'.format(
                    get_spinner_character(),
                    image,
                    format_size(outfp.tell()),
                    (format_size(image_size) if image_size else 'unknown size'),
                )
                print(status_text.ljust(width - 1), end='\r')
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, 'docker save ' + image)
    click.secho('    {} exported: {}'.format(
        image,
        format_size(os.stat(output_path).st_size),
    ), fg='green')
