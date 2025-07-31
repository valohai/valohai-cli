import os
from subprocess import check_output

import pytest
from click import termui

import valohai_cli.packager as pkg
from tests.stub_git import StubGit
from valohai_cli.exceptions import ConfigurationError, NoCommit, PackageTooLarge
from valohai_cli.git import describe_current_commit


def write_temp_files(
    tmpdir,
    *,
    with_yaml: bool = True,
    with_gitignore: bool = True,
    with_vhignore: bool = False,
    large_file_size: int = 0,
):
    if with_gitignore:
        tmpdir.join(".gitignore").write_text("a*\n", "utf8")  # ignore all files starting with a
    if with_vhignore:
        tmpdir.join(".vhignore").write_text("kah*\n", "utf8")  # ignore all files starting with kah

    tmpdir.join("asbestos").write_text("scary", "utf8")
    tmpdir.join("kahvikuppi").write_text("mmmm, coffee", "utf8")
    tmpdir.join(".hiddenfile").write_text("where is it", "utf8")
    if with_yaml:
        tmpdir.join("valohai.yaml").write_text("this file is required", "utf8")
    if large_file_size:
        pth = str(tmpdir.join("large_file.dat"))
        with open(pth, "wb") as outfp:
            outfp.truncate(large_file_size)
        assert os.stat(pth).st_size == large_file_size


def get_tar_files(tarball):
    return set(check_output(f"tar tf {tarball}", shell=True).decode("utf8").splitlines())


def get_expected_filenames(original_set: set[str], *, with_gitignore, with_vhignore) -> set[str]:
    new_set = original_set.copy()
    if with_vhignore:  # vhignore stops kahvikuppi
        new_set.discard("kahvikuppi")
    if with_gitignore:  # gitignore stops asbestos
        new_set.discard("asbestos")
    return new_set


@pytest.mark.parametrize("with_commit", (False, True))
@pytest.mark.parametrize("with_vhignore", (False, True))
def test_package_git(tmpdir, with_commit, with_vhignore):
    stub_git = StubGit(tmpdir)
    stub_git.init()
    write_temp_files(tmpdir, with_vhignore=with_vhignore)
    if with_commit:
        stub_git.add_all()
        stub_git.commit()
        assert describe_current_commit(stub_git.dir_str)
    else:
        with pytest.raises(NoCommit):
            describe_current_commit(stub_git.dir_str)
    tarball = pkg.package_directory(directory=stub_git.dir_str, yaml_path="valohai.yaml")
    # the dotfile and asbestos do not appear
    assert get_tar_files(tarball) == get_expected_filenames(
        {"kahvikuppi", "valohai.yaml"},
        with_vhignore=with_vhignore,
        with_gitignore=True,
    )


@pytest.mark.parametrize("with_gitignore", (False, True))
@pytest.mark.parametrize("with_vhignore", (False, True))
def test_package_no_git(tmpdir, with_gitignore, with_vhignore):
    write_temp_files(tmpdir, with_gitignore=with_gitignore, with_vhignore=with_vhignore)
    tarball = pkg.package_directory(directory=str(tmpdir), yaml_path="valohai.yaml")
    expected_filenames = get_expected_filenames(
        {"asbestos", "kahvikuppi", "valohai.yaml"},
        with_vhignore=with_vhignore,
        with_gitignore=with_gitignore,
    )
    assert get_tar_files(tarball) == expected_filenames


def test_package_requires_yaml(tmpdir):
    write_temp_files(tmpdir, with_yaml=False)
    with pytest.raises(ConfigurationError):
        pkg.package_directory(directory=str(tmpdir), yaml_path="valohai.yaml")


def test_file_soft_size_warn(tmpdir, capsys, monkeypatch):
    monkeypatch.setattr(termui, "visible_prompt_func", lambda x: "y\n")
    write_temp_files(tmpdir, with_yaml=True, large_file_size=int(pkg.FILE_SIZE_WARN_THRESHOLD + 50))
    pkg.package_directory(directory=str(tmpdir), yaml_path="valohai.yaml")
    _out, err = capsys.readouterr()
    assert "Large file large_file.dat" in err


@pytest.mark.parametrize(
    "threshold",
    (
        "UNCOMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD",
        "COMPRESSED_PACKAGE_SIZE_HARD_THRESHOLD",
    ),
)
def test_package_hard_size_fail(tmpdir, monkeypatch, threshold):
    monkeypatch.setattr(pkg, threshold, 200)
    write_temp_files(tmpdir, with_yaml=True, with_gitignore=False, large_file_size=10000)
    with pytest.raises(PackageTooLarge):
        pkg.package_directory(directory=str(tmpdir), yaml_path="valohai.yaml")


def test_package_file_count_hard_fail(tmpdir, monkeypatch):
    # Should not fail here
    monkeypatch.setattr(pkg, "FILE_COUNT_HARD_THRESHOLD", 3)
    write_temp_files(tmpdir, with_yaml=True, with_gitignore=False)
    pkg.package_directory(directory=str(tmpdir), yaml_path="valohai.yaml")

    # With threshold of 2, should fail for 3 files
    monkeypatch.setattr(pkg, "FILE_COUNT_HARD_THRESHOLD", 2)
    with pytest.raises(PackageTooLarge):
        pkg.package_directory(directory=str(tmpdir), yaml_path="valohai.yaml")


def test_single_file_packaged_correctly(tmpdir):
    tmpdir.join("valohai.yaml").write_text("this file is required", "utf8")
    tarball = pkg.package_directory(directory=str(tmpdir), yaml_path="valohai.yaml")
    assert get_tar_files(tarball) == {"valohai.yaml"}


def test_no_files_in_rootdir(tmpdir):
    tmpdir.mkdir("subway").join("asdf.bat").write_text("this file is required", "utf8")
    tarball = pkg.package_directory(directory=str(tmpdir), yaml_path="valohai.yaml", validate=False)
    assert get_tar_files(tarball) == {"subway/asdf.bat"}


def test_vhignore_entire_directory(tmp_path):
    (tmp_path / ".vhignore").write_text("data/\n")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "file1").write_text("this file is ignored")
    (tmp_path / "hello.py").write_text('print("hello")')
    (tmp_path / "valohai.yaml").write_text("")
    tarball = pkg.package_directory(directory=str(tmp_path), yaml_path="valohai.yaml")
    assert get_tar_files(tarball) == {"hello.py", "valohai.yaml"}
