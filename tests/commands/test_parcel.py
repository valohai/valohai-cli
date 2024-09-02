import os

import pytest
import requests_mock

from tests.stub_git import StubGit
from valohai_cli.commands.parcel import parcel
from valohai_cli.utils import get_project_directory


@pytest.mark.slow
def test_parcel(runner, logged_in_and_linked, tmpdir):
    stub_git = StubGit(get_project_directory())
    stub_git.init()
    stub_git.write("my_script.sh", content="echo hello")
    stub_git.write(
        "valohai.yaml",
        content="""
- step:
    name: step1
    image: busybox
    command: sh my_script.sh
- step:
    name: step2
    image: alpine
    command: sh my_script.sh bar
""",
    )
    stub_git.commit()

    output_dir = str(tmpdir.mkdir("output"))

    with requests_mock.mock():
        result = runner.invoke(parcel, ["-d", output_dir])
        assert result.exit_code == 0

    assert set(os.listdir(output_dir)) == {
        "docker-alpine.tar",
        "docker-busybox.tar",
        "git-repo.bundle",
        "python-archives",
        "unparcel.sh",
    }

    with open(os.path.join(output_dir, "git-repo.bundle"), "rb") as bundle_fp:
        assert bundle_fp.read(32).startswith(b"# v2 git bundle")
