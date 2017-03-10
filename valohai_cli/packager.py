import gzip
import os
import tarfile
import tempfile
from subprocess import check_output

import click

from valohai_cli.exceptions import ConfigurationError


def package_directory(dir, progress=False):
    files = get_files_for_package(dir)

    if 'valohai.yaml' not in files:
        raise ConfigurationError('valohai.yaml missing from {}'.format(dir))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.tgz', prefix='valohai-cli-') as fp:
        # Manually creating the gzipfile to force mtime to 0.
        with gzip.GzipFile('data.tar', mode='w', fileobj=fp, mtime=0) as gzf:
            with tarfile.open(name='data.tar', mode='w', fileobj=gzf) as tarball:
                progress_bar = click.progressbar(
                    files,
                    show_pos=True,
                    item_show_func=lambda i: ('Packaging: %s' % i if i else ''),
                    width=0,
                )
                if not progress:
                    progress_bar.is_hidden = True

                with progress_bar:
                    for file in progress_bar:
                        tarball.add(
                            name=os.path.join(dir, file),
                            arcname=file,
                        )
    return fp.name


def get_files_for_package(dir, allow_git=True):
    if allow_git and os.path.exists(os.path.join(dir, '.git')):
        # We have .git, so we can use Git to figure out a file list of nonignored files
        files = [
            line.decode('utf-8')
            for line
            in check_output('git ls-files --exclude-standard -ocz', cwd=dir, shell=True).split(b'\0')
            if line and not line.startswith(b'.')
        ]
    else:
        # Otherwise, just package up everything that doesn't have a . prefix
        files = []
        for dirpath, dirnames, filenames in os.walk(dir):
            dirnames[:] = [dirname for dirname in dirnames if not dirname.startswith('.')]
            files.extend([os.path.join(dirpath, filename) for filename in filenames if not filename.startswith('.')])
        common_prefix = (
            os.path.commonprefix(files)
            if len(files) > 1 else
            os.path.dirname(files[0]) + os.sep
        )
        files = [filename[len(common_prefix):] for filename in files]
    files.sort()
    return files
