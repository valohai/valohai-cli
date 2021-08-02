import os
import subprocess

import pytest
import requests_mock

from valohai_cli.commands.parcel import parcel
from valohai_cli.utils import get_project_directory


def create_fake_project(dir):
    with open(os.path.join(dir, 'my_script.sh'), 'w') as script_fp:
        script_fp.write('echo hello')
    with open(os.path.join(dir, 'valohai.yaml'), 'w') as config_fp:
        config_fp.write('''
- step:
    name: step1
    image: busybox
    command: sh my_script.sh
- step:
    name: step2
    image: alpine
    command: sh my_script.sh bar
''')
    subprocess.check_call(' && '.join([
        'git init',
        'git config user.email "robot@example.com"',
        'git config user.name "Robot"',
        'git add .',
        'git commit -m commit',
    ]), cwd=dir, shell=True)


@pytest.mark.slow
def test_parcel(runner, logged_in_and_linked, tmpdir):
    input_dir = get_project_directory()
    create_fake_project(input_dir)
    output_dir = str(tmpdir.mkdir('output'))

    with requests_mock.mock():
        result = runner.invoke(parcel, ['-d', output_dir])
        assert result.exit_code == 0

    assert set(os.listdir(output_dir)) == {
        'docker-alpine.tar',
        'docker-busybox.tar',
        'git-repo.bundle',
        'python-archives',
        'unparcel.sh',
    }

    with open(os.path.join(output_dir, 'git-repo.bundle'), 'rb') as bundle_fp:
        assert bundle_fp.read(32).startswith(b'# v2 git bundle')
