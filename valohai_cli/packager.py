import fnmatch
import gzip
import os
import subprocess
import tarfile
import tempfile
from collections import namedtuple
from enum import Enum
from subprocess import check_output
from typing import IO, Dict, Iterable, List, Tuple

import click
import gitignorant

from valohai_cli.exceptions import ConfigurationError, PackageTooLarge
from valohai_cli.messages import info, warn
from valohai_cli.utils.file_size_format import filesizeformat

FILE_SIZE_WARN_THRESHOLD = 50 * 1024 * 1024
FILE_COUNT_HARD_THRESHOLD = 10000
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

PackageFileInfo = namedtuple('PackageFileInfo', ('source_path', 'stat'))


class GitUsage(Enum):
    NONE = 0
    GITIGNORE_WITHOUT_GIT = 1
    GIT_LS_FILES = 2


class VhIgnoreUsage(Enum):
    NONE = 0
    VHIGNORE = 1


def package_directory(*, directory: str, yaml_path: str, progress: bool = False, validate: bool = True) -> str:
    file_stats = get_files_for_package(directory)

    if validate and yaml_path not in file_stats:
        raise ConfigurationError(f'configuration file {yaml_path} missing from {directory}')

    if validate:
        package_size_warnings = validate_package_size(file_stats)
        if package_size_warnings:
            for warning in package_size_warnings:
                click.secho(f'* {warning}', err=True)
            click.secho(PACKAGE_SIZE_HELP, err=True)
            click.confirm('Continue packaging anyway?', default=True, abort=True, prompt_suffix='', err=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.tgz', prefix='valohai-cli-') as fp:
        package_files_into(fp, file_stats, progress=progress)
        total_compressed_size = fp.tell()

    if validate and total_compressed_size >= COMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD:
        raise PackageTooLarge(
            f'The total compressed size of the package is {filesizeformat(total_compressed_size)}, '
            f'which exceeds the threshold {filesizeformat(COMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD)}'
        )
    return fp.name


def package_files_into(
    dest_fp: IO[bytes],
    file_stats: Dict[str, PackageFileInfo],
    progress: bool = False,
) -> None:
    """
    Package (gzipped tarball) files from `file_stats` (which is a dict mapping names within the package
    to their PackageFileInfo tuples) into the open writable binary file `dest_fp`.

    The dict could look like this:

    {
      'valohai.yaml': PackageFileInfo(source_path='/my/tmp/valohai.yaml', stat=...),
      'train.py': PackageFileInfo(source_path='/my/somewhere/else/train.py', stat=...),
      'data/foo.dat': PackageFileInfo(source_path='/tmp/big.data', stat=...),
    }

    :param dest_fp: Target file descriptor
    :param file_stats: Dict of files to infos
    :param progress: Whether to show progress
    :return:
    """

    files = sorted(file_stats.keys())

    # Manually creating the gzipfile to force mtime to 0.
    with gzip.GzipFile('data.tar', mode='w', fileobj=dest_fp, mtime=0) as gzf:  # noqa: SIM117
        with tarfile.open(name='data.tar', mode='w', fileobj=gzf) as tarball:  # type: ignore[arg-type]
            progress_bar = click.progressbar(
                files,
                show_pos=True,
                item_show_func=lambda i: (f'Packaging: {i}' if i else ''),
                width=0,
            )
            if not progress:
                progress_bar.is_hidden = True

            with progress_bar:
                for file in progress_bar:
                    pfi = file_stats[file]
                    if os.path.isfile(pfi.source_path):
                        tarball.add(name=pfi.source_path, arcname=file)
    dest_fp.flush()


def _get_files_with_git(dir: str) -> Iterable[Tuple[str, str]]:
    paths_seen = set()
    commands = [
        'git ls-files --exclude-standard -ocz',
    ]

    # Check whether a gitmodules file exists; if so, also do a `--recurse-submodules` pass
    # to gather files in submodules.  Untracked files in submodules will not be considered,
    # since `--recurse-submodules` does not support `-o`.
    gitmodules_file = os.path.join(dir, '.gitmodules')
    if os.path.isfile(gitmodules_file):
        commands.append('git ls-files --exclude-standard --recurse-submodules -cz')

    for command in commands:
        for line in check_output(command, cwd=dir, shell=True).split(b'\0'):
            if line.startswith(b'.'):
                continue
            file = line.decode('utf-8')
            path = os.path.join(dir, file)
            if path not in paths_seen:
                paths_seen.add(path)
                yield (file, path)


def _get_files_walk(dir: str) -> Iterable[Tuple[str, str]]:
    for dirpath, dirnames, filenames in os.walk(dir):
        dirnames[:] = [dirname for dirname in dirnames if not dirname.startswith('.')]
        for filename in filenames:
            if filename.startswith('.'):
                continue
            filename = os.path.join(dirpath, filename)
            file_abs_path = os.path.join(dir, filename)
            file_rel_path = filename[len(dir):].lstrip(os.sep)
            yield (file_rel_path, file_abs_path)


def _get_files_inner(dir: str, allow_git: bool = True) -> Tuple[GitUsage, Iterable[Tuple[str, str]]]:
    # Inner, pre-vhignore-supporting generator function...
    gitignore_path = os.path.join(dir, '.gitignore')

    if allow_git:
        if os.path.exists(os.path.join(dir, '.git')):
            # We have .git, so we can try to use Git to figure out a file list of nonignored files
            try:
                return (GitUsage.GIT_LS_FILES, _get_files_with_git(dir))  # return the generator
            except subprocess.CalledProcessError as cpe:
                warn(f'.git exists, but we could not use git ls-files (error {cpe.returncode}), falling back to non-git')

        # Limited support of .gitignore even without git
        if os.path.exists(gitignore_path):
            with open(gitignore_path) as gitignore_file:
                gitignore_rules = list(gitignorant.parse_gitignore_file(gitignore_file))
            if gitignore_rules:
                return (
                    GitUsage.GITIGNORE_WITHOUT_GIT,
                    (p for p in _get_files_walk(dir) if not gitignorant.check_path_match(gitignore_rules, p[0])),
                )

    return (GitUsage.NONE, _get_files_walk(dir))  # return the generator


def _get_files(dir: str, allow_git: bool = True) -> Tuple[GitUsage, VhIgnoreUsage, Iterable[Tuple[str, str]]]:
    git_usage, ftup_gen = _get_files_inner(dir, allow_git=allow_git)
    vhignore_path = os.path.join(dir, '.vhignore')

    if os.path.isfile(vhignore_path):
        with open(vhignore_path) as vhignore_file:
            vhignore_rules = list(gitignorant.parse_gitignore_file(vhignore_file))
        if vhignore_rules:
            return (
                git_usage,
                VhIgnoreUsage.VHIGNORE,
                (p for p in ftup_gen if not gitignorant.check_path_match(vhignore_rules, p[0])),
            )
    return (
        git_usage,
        VhIgnoreUsage.NONE,
        ftup_gen,
    )


def is_valid_path(path: str, ignore_patterns: Iterable[str]) -> bool:
    return all(
        (not fnmatch.fnmatch(path, pat) or pat in path)
        for pat in ignore_patterns
    )


def get_files_for_package(
    dir: str,
    allow_git: bool = True,
    ignore_patterns: Iterable[str] = (),
) -> Dict[str, PackageFileInfo]:
    """
    Get files to package for ad-hoc packaging from the file system.

    :param dir: The source directory. Probably a working copy root or similar.
    :param allow_git: Whether to allow usage of `git ls-files`, if available, for packaging.
    :param ignore_patterns: List of ignored patterns.
    :return:
    """
    files_and_paths = []
    git_usage, vhignore_usage, ftup_generator = _get_files(dir, allow_git=allow_git)

    for ftup in ftup_generator:
        if ignore_patterns and not is_valid_path(ftup[1], ignore_patterns):
            continue
        files_and_paths.append(ftup)
        if len(files_and_paths) > FILE_COUNT_HARD_THRESHOLD:
            raise PackageTooLarge(
                f'Trying to package too many files (threshold: {FILE_COUNT_HARD_THRESHOLD}).')

    info(_get_packaging_info_message(len(files_and_paths), git_usage, vhignore_usage))

    output_stats = {}
    for file, file_path in files_and_paths:
        try:
            output_stats[file] = PackageFileInfo(source_path=file_path, stat=os.stat(file_path))
        except FileNotFoundError:
            # A file was reported by git-ls but not found on disk - don't try to package it.
            pass
    return output_stats


def _get_packaging_info_message(count: int, git_usage: GitUsage, vhignore_usage: VhIgnoreUsage) -> str:
    and_vhignore_bit = (' (with .vhignore)' if vhignore_usage == VhIgnoreUsage.VHIGNORE else '')
    if git_usage == GitUsage.GIT_LS_FILES:
        return f'Used git{and_vhignore_bit} to find {count} files to package'
    elif git_usage == GitUsage.GITIGNORE_WITHOUT_GIT:
        return (
            f'Used .gitignore (with limited support){and_vhignore_bit} '
            f'to find {count} files to package. '
            f'Create a git repository for full .gitignore support.'
        )
    return (
        f'Walked filesystem{and_vhignore_bit} and '
        f'found {count} files to package. '
        f'Git or .gitignore not available.'
    )


def validate_package_size(file_stats: Dict[str, PackageFileInfo]) -> List[str]:
    warnings = []
    total_uncompressed_size = 0
    for file, pfi in sorted(file_stats.items()):
        stat = pfi.stat
        total_uncompressed_size += stat.st_size
        if stat.st_size >= FILE_SIZE_WARN_THRESHOLD:
            warnings.append(f'Large file {file}: {filesizeformat(stat.st_size)}')
    if total_uncompressed_size >= UNCOMPRESSED_PACKAGE_SIZE_SOFT_THRESHOLD:
        warnings.append(f'The total uncompressed size of the package is {filesizeformat(total_uncompressed_size)}')
    if total_uncompressed_size >= UNCOMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD:
        raise PackageTooLarge(
            f'The total uncompressed size of the package is {filesizeformat(total_uncompressed_size)}, '
            f'which exceeds the threshold {filesizeformat(UNCOMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD)}'
        )
    return warnings
