import os

import pytest

from tests.commands.yaml.utils import build_args
from tests.fixtures.code import PYTHON_SOURCE, PYTHON_SOURCE_USING_VALOHAI_UTILS
from tests.fixtures.config import CONFIG_YAML
from valohai_cli.commands.yaml.step import step
from valohai_cli.ctx import get_project


@pytest.mark.parametrize("yaml_path", ["bark.yaml", None])
def test_yaml(runner, logged_in_and_linked, yaml_path):
    # Try to generate YAML from random .py source code
    project = get_project()
    source_path = os.path.join(project.directory, "mysnake.py")
    yaml_path = yaml_path or project.get_yaml_path()
    with open(source_path, "w") as python_fp:
        python_fp.write(PYTHON_SOURCE)
    args = build_args(source_path, yaml_path)
    rv = runner.invoke(step, args, catch_exceptions=True)
    assert isinstance(rv.exception, ValueError)

    # Generate YAML from .py source code that is using valohai-utils
    with open(source_path, "w") as python_fp:
        python_fp.write(PYTHON_SOURCE_USING_VALOHAI_UTILS)
    args = build_args(source_path, yaml_path)
    rv = runner.invoke(step, args, catch_exceptions=False)
    assert f"{yaml_path} generated." in rv.output

    # Update existing YAML from source code
    config_path = project.get_config_filename(yaml_path=yaml_path)
    with open(config_path, "w") as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    args = build_args(source_path, yaml_path)
    rv = runner.invoke(step, args, catch_exceptions=False)
    assert f"{yaml_path} updated." in rv.output

    # Try the same update again
    rv = runner.invoke(step, args, catch_exceptions=False)
    assert f"{yaml_path} already up-to-date." in rv.output
