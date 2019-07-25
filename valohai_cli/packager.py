import gzip
import os
import subprocess
import tarfile
import tempfile
from subprocess import check_output

import click

from valohai_cli.exceptions import ConfigurationError, PackageTooLarge
from valohai_cli.messages import info, warn
from valohai_cli.utils.file_size_format import filesizeformat

FILE_SIZE_WARN_THRESHOLD = 50 * 1024 * 1024
UNCOMPRESSED_PACKAGE_SIZE_SOFT_THRESHOLD = 150 * 1024 * 1024
COMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD = 1000 * 1024 * 1024

# We guess that Gzip may help halve the package size -
# if the package is actually all source code, it will probably help more.
UNCOMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD = COMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD / 0.5

PACKAGE_SIZE_HELP = '''
It's generally not a good idea to have large files in your working copy,
as most version control systems, Git included, are optimized to work with
code, not data.

Data files such as pretraining data or checkpoint files should be managed
with the Valohai inputs system instead for increased performance.

If you are using Git, consider `git rm`ing the large files and adding
their patterns to your `.gitignore` file.

You can disable this validation with the `--no-validate-adhoc` option.
'''


def package_directory(dir, progress=False, validate=True):
    file_stats = get_files_for_package(dir)

    if 'valohai.yaml' not in file_stats:
        raise ConfigurationError('valohai.yaml missing from {}'.format(dir))

    if validate:
        package_size_warnings = validate_package_size(file_stats)
        if package_size_warnings:
            for warning in package_size_warnings:
                click.secho('* ' + warning, err=True)
            click.secho(PACKAGE_SIZE_HELP, err=True)
            click.confirm('Continue packaging anyway?', default=True, abort=True, prompt_suffix='', err=True)

    files = sorted(file_stats.keys())

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
                        path = os.path.join(dir, file)
                        if os.path.isfile(path):
                            tarball.add(name=path, arcname=file)
        fp.flush()
        total_compressed_size = fp.tell()

    if validate and total_compressed_size >= COMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD:
        raise PackageTooLarge(
            'The total compressed size of the package is {size}, which exceeds the threshold {threshold}'.format(
                size=filesizeformat(total_compressed_size),
                threshold=filesizeformat(COMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD),
            ))
    return fp.name


def get_files_for_package(dir, allow_git=True):
    files = None
    if allow_git and os.path.exists(os.path.join(dir, '.git')):
        # We have .git, so we can try to use Git to figure out a file list of nonignored files
        try:
            files = [
                line.decode('utf-8')
                for line
                in check_output('git ls-files --exclude-standard -ocz', cwd=dir, shell=True).split(b'\0')
                if line and not line.startswith(b'.')
            ]
            info('Used git to find {n} files to package'.format(n=len(files)))
        except subprocess.CalledProcessError as cpe:
            warn('.git exists, but we could not use git ls-files (error %d), falling back to non-git' % cpe.returncode)

    if files is None:
        # We failed to use git for packaging, or didn't want to -
        # just package up everything that doesn't have a . prefix
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
        info('Git not available, found {n} files to package'.format(n=len(files)))
    return {file: os.stat(os.path.join(dir, file)) for file in files}


def validate_package_size(file_stats):
    warnings = []
    total_uncompressed_size = 0
    for file, stat in sorted(file_stats.items()):
        total_uncompressed_size += stat.st_size
        if stat.st_size >= FILE_SIZE_WARN_THRESHOLD:
            warnings.append('Large file {file}: {size}'.format(
                file=file,
                size=filesizeformat(stat.st_size),
            ))
    if total_uncompressed_size >= UNCOMPRESSED_PACKAGE_SIZE_SOFT_THRESHOLD:
        warnings.append('The total uncompressed size of the package is {size}'.format(
            size=filesizeformat(total_uncompressed_size),
        ))
    if total_uncompressed_size >= UNCOMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD:
        raise PackageTooLarge(
            'The total uncompressed size of the package is {size}, which exceeds the threshold {threshold}'.format(
                size=filesizeformat(total_uncompressed_size),
                threshold=filesizeformat(UNCOMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD),
            ))
    return warnings
