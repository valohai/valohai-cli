import os
import shutil
import subprocess
import sys
import time
from typing import Iterable, List, Optional

import click

from valohai_cli.ctx import get_project
from valohai_cli.git import expand_commit_id
from valohai_cli.messages import success
from valohai_cli.models.project import Project
from valohai_cli.tui import get_spinner_character
from valohai_cli.utils import ensure_makedirs, sanitize_filename
from valohai_cli.utils.file_size_format import filesizeformat

MINIMUM_VALOHAI_LOCAL_RUN_VERSION = '0.2.1'

UNPARCEL_SCRIPT = r"""
#!/bin/bash
WORKING_COPY_DIR=$(mktemp -dut parcel-working-copy-XXXXXX)
(
set -ex
find . -name 'docker*tar' -exec docker load -i '{}' ';'
[ -d python-archives ] && pip3 install --user python-archives/*
[ -f git-repo.bundle ] && git clone ./git-repo.bundle "$WORKING_COPY_DIR"
[ -f git-commit.tar ] && mkdir "$WORKING_COPY_DIR" && tar -xvf ./git-commit.tar -C "$WORKING_COPY_DIR"
[ -f code.tar ] && mkdir "$WORKING_COPY_DIR" && tar -xvf ./code.tar -C "$WORKING_COPY_DIR"
)
cd $WORKING_COPY_DIR
""".strip()


def print_parcel_progress(text: str) -> None:
    click.secho(f'::: {text}', bold=True, fg='cyan', err=True)


@click.command()
@click.option('-d', '--destination', type=click.Path(file_okay=False, dir_okay=True), required=False, help='Destination directory')
@click.option('-c', '--commit', help='Commit to read required Docker image IDs from')
@click.option(
    '--code',
    type=click.Choice(['bundle', 'archive', 'tarball', 'none']),
    default='bundle',
    help='Package code as a full Git bundle, an archive of Git HEAD, a tarball of the directory or not at all?',
)
@click.option('--docker-images/--no-docker-images', default=True, help='Package Docker images?')
@click.option('--valohai-local-run/--no-valohai-local-run', default=True, help='Download valohai-local-run + deps?')
@click.option('--unparcel-script/--no-unparcel-script', default=True, help='Add unparcel script?')
def parcel(
    destination: Optional[str],
    commit: Optional[str],
    code: str,
    valohai_local_run: bool,
    docker_images: bool,
    unparcel_script: bool,
) -> None:
    """
    Package a project for offline execution. (Experimental)
    """
    project = get_project(require=True)

    if not destination:
        destination = sanitize_filename(f'{project.name}-parcel-{time.strftime("%Y%m%d-%H%M%S")}')

    click.echo(
        f'Packing {click.style(project.name, bold=True, fg="blue")} '
        f'to directory {click.style(destination, bold=True, fg="green")}'
    )

    ensure_makedirs(destination)

    extra_docker_images: List[str] = []

    if code in ('bundle', 'archive', 'tarball'):
        export_code(project, destination, mode=code)

    if valohai_local_run:
        export_valohai_local_run(destination)

    if docker_images:
        export_docker_images(project, destination, commit, extra_docker_images)

    if unparcel_script:
        write_unparcel_script(destination)

    success(f'Parcel {destination} created!')


def export_valohai_local_run(destination: str) -> None:
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


def write_unparcel_script(destination: str) -> None:
    unparcel_sh_path = os.path.join(destination, 'unparcel.sh')
    print_parcel_progress(f'Creating unparcel script {unparcel_sh_path}')
    with open(unparcel_sh_path, 'w') as outf:
        outf.write(UNPARCEL_SCRIPT)
    os.chmod(unparcel_sh_path, os.stat(unparcel_sh_path).st_mode | 0o700)


def export_code(project: Project, destination: str, mode: str) -> None:
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
                f'--exclude={os.path.basename(destination)}',  # In case we're being run in the same dir
                '.',  # Correct directory taken care of with cwd
            ],
            cwd=project.directory,
        )
    else:  # pragma: no cover
        raise NotImplementedError('...')


def get_docker_image_size(image: str) -> Optional[int]:
    """
    Try to get the size of the given Docker image in bytes.
    :param image: The image name.
    :return: Number of bytes, or None if not available.
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


def export_docker_images(
    project: Project,
    destination: str,
    commit: Optional[str],
    extra_docker_images: Iterable[str] = (),
) -> None:
    commit = expand_commit_id(project.directory, commit=(commit or 'HEAD'))
    docker_images = {step.image for step in project.get_config(commit).steps.values()}
    docker_images |= set(extra_docker_images)
    n = len(docker_images)
    for i, image in enumerate(docker_images, 1):
        output_path = os.path.join(destination, sanitize_filename(f'docker-{image}.tar'))
        if image not in extra_docker_images:
            print_parcel_progress(f'::: Pulling image {i}/{n} ({image})')
            subprocess.check_call(['docker', 'pull', image])
        print_parcel_progress(f'::: Exporting image {i}/{n} ({image})')
        export_docker_image(image, output_path)


def export_docker_image(image: str, output_path: str, print_progress: bool = True) -> None:
    """
    Export the Docker image `image` to the tar file `output_path`,
    with visual progress.

    :param image: Image specifier
    :param output_path: Output pathname
    """

    proc = subprocess.Popen(['docker', 'save', image], bufsize=-1, stdout=subprocess.PIPE)
    if not proc.stdout:
        raise RuntimeError("No output stream")
    print_progress = (print_progress and sys.stdout.isatty())
    # Don't bother with acquiring the image size if we're not going to print it anyway
    image_size = (get_docker_image_size(image) if print_progress else None)
    with open(output_path, 'wb') as outfp:
        if print_progress:
            click.echo('Initializing export...\r', nl=False, err=True)
        while proc.poll() is None:
            chunk = proc.stdout.read(1048576)
            if not chunk:
                break
            outfp.write(chunk)
            if print_progress:
                width = shutil.get_terminal_size()[0]
                size_fmt = (filesizeformat(image_size) if image_size else 'unknown size')
                pos_fmt = filesizeformat(outfp.tell())
                status_text = f'{get_spinner_character()} {image}: {pos_fmt} / {size_fmt}'
                click.echo(status_text.ljust(width - 1), nl=False, err=True)
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, 'docker save ' + image)
    success(f'{image} exported: {filesizeformat(os.stat(output_path).st_size)}')
