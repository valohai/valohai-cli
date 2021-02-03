import os
from subprocess import check_call, check_output

import pytest
from click import termui

import valohai_cli.packager as pkg
from valohai_cli.exceptions import ConfigurationError, NoCommit, PackageTooLarge
from valohai_cli.git import describe_current_commit


def write_temp_files(tmpdir, with_yaml=True, large_file_size=0):
    tmpdir.join('.gitignore').write_text('a*\n', 'utf8')  # ignore all files starting with a
    tmpdir.join('asbestos').write_text('scary', 'utf8')
    tmpdir.join('kahvikuppi').write_text('mmmm, coffee', 'utf8')
    tmpdir.join('.hiddenfile').write_text('where is it', 'utf8')
    if with_yaml:
        tmpdir.join('valohai.yaml').write_text('this file is required', 'utf8')
    if large_file_size:
        pth = str(tmpdir.join('large_file.dat'))
        with open(pth, 'wb') as outfp:
            outfp.truncate(large_file_size)
        assert os.stat(pth).st_size == large_file_size


def get_tar_files(tarball):
    return set(check_output('tar tf %s' % tarball, shell=True).decode('utf8').splitlines())


@pytest.mark.parametrize('with_commit', (False, True))
def test_package_git(tmpdir, with_commit):
    check_call('git init', cwd=str(tmpdir), shell=True)
    write_temp_files(tmpdir)
    if with_commit:
        check_call('git add .', cwd=str(tmpdir), shell=True)
        check_call('git commit -m test', cwd=str(tmpdir), shell=True)
        assert describe_current_commit(str(tmpdir))
    else:
        with pytest.raises(NoCommit):
            describe_current_commit(str(tmpdir))
    tarball = pkg.package_directory(str(tmpdir))
    # the dotfile and asbestos do not appear
    assert get_tar_files(tarball) == {'kahvikuppi', 'valohai.yaml'}


def test_package_no_git(tmpdir):
    write_temp_files(tmpdir)
    tarball = pkg.package_directory(str(tmpdir))
    # the dotfile is gone, but there's nothing to stop the asbestos
    assert get_tar_files(tarball) == {'asbestos', 'kahvikuppi', 'valohai.yaml'}


def test_package_requires_yaml(tmpdir):
    write_temp_files(tmpdir, with_yaml=False)
    with pytest.raises(ConfigurationError):
        pkg.package_directory(str(tmpdir))


def test_file_soft_size_warn(tmpdir, capsys, monkeypatch):
    monkeypatch.setattr(termui, 'visible_prompt_func', lambda x: 'y\n')
    write_temp_files(tmpdir, with_yaml=True, large_file_size=int(pkg.FILE_SIZE_WARN_THRESHOLD + 50))
    pkg.package_directory(str(tmpdir))
    out, err = capsys.readouterr()
    assert 'Large file large_file.dat' in err


@pytest.mark.parametrize('threshold', (
    'UNCOMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD',
    'COMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD',
))
def test_package_hard_size_fail(tmpdir, monkeypatch, threshold):
    monkeypatch.setattr(pkg, threshold, 200)
    write_temp_files(tmpdir, with_yaml=True, large_file_size=10000)
    with pytest.raises(PackageTooLarge):
        pkg.package_directory(str(tmpdir))


def test_package_file_count_hard_fail(tmpdir, monkeypatch):
    # Should not fail here
    monkeypatch.setattr(pkg, 'FILE_COUNT_HARD_THRESHOLD', 3)
    write_temp_files(tmpdir, with_yaml=True)
    pkg.package_directory(str(tmpdir))

    # With threshold of 2, should fail for 3 files
    monkeypatch.setattr(pkg, 'FILE_COUNT_HARD_THRESHOLD', 2)
    with pytest.raises(PackageTooLarge):
        pkg.package_directory(str(tmpdir))


def test_single_file_packaged_correctly(tmpdir):
    tmpdir.join('valohai.yaml').write_text('this file is required', 'utf8')
    tarball = pkg.package_directory(str(tmpdir))
    assert get_tar_files(tarball) == {'valohai.yaml'}


def test_no_files_in_rootdir(tmpdir):
    tmpdir.mkdir('subway').join('asdf.bat').write_text('this file is required', 'utf8')
    tarball = pkg.package_directory(str(tmpdir), validate=False)
    assert get_tar_files(tarball) == {'subway/asdf.bat'}
