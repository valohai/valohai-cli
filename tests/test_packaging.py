from __future__ import unicode_literals

from subprocess import check_call, check_output

import pytest

from valohai_cli.exceptions import ConfigurationError
from valohai_cli.packager import package_directory


def write_temp_files(tmpdir, with_yaml=True):
    tmpdir.join('.gitignore').write_text('a*\n', 'utf8')  # ignore all files starting with a
    tmpdir.join('asbestos').write_text('scary', 'utf8')
    tmpdir.join('kahvikuppi').write_text('mmmm, coffee', 'utf8')
    tmpdir.join('.hiddenfile').write_text('where is it', 'utf8')
    if with_yaml:
        tmpdir.join('valohai.yaml').write_text('this file is required', 'utf8')


def get_tar_files(tarball):
    return set(check_output('tar tf %s' % tarball, shell=True).decode('utf8').splitlines())


def test_package_git(tmpdir):
    check_call('git init', cwd=str(tmpdir), shell=True)
    write_temp_files(tmpdir)
    tarball = package_directory(str(tmpdir))
    # the dotfile and asbestos do not appear
    assert get_tar_files(tarball) == {'kahvikuppi', 'valohai.yaml'}


def test_package_no_git(tmpdir):
    write_temp_files(tmpdir)
    tarball = package_directory(str(tmpdir))
    # the dotfile is gone, but there's nothing to stop the asbestos
    assert get_tar_files(tarball) == {'asbestos', 'kahvikuppi', 'valohai.yaml'}


def test_package_requires_yaml(tmpdir):
    write_temp_files(tmpdir, with_yaml=False)
    with pytest.raises(ConfigurationError):
        package_directory(str(tmpdir))


def test_single_file_packaged_correctly(tmpdir):
    tmpdir.join('valohai.yaml').write_text('this file is required', 'utf8')
    tarball = package_directory(str(tmpdir))
    assert get_tar_files(tarball) == {'valohai.yaml'}
