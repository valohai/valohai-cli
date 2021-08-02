import os

from tests.fixture_data import CONFIG_YAML, PYTHON_SOURCE, PYTHON_SOURCE_USING_VALOHAI_UTILS
from valohai_cli.commands.yaml.step import step
from valohai_cli.ctx import get_project


def test_yaml(runner, logged_in_and_linked):
    # Try to generate YAML from random .py source code
    source_path = os.path.join(get_project().directory, 'mysnake.py')
    with open(source_path, 'w') as python_fp:
        python_fp.write(PYTHON_SOURCE)
    args = ([source_path])
    rv = runner.invoke(step, args, catch_exceptions=True)
    assert isinstance(rv.exception, ValueError)

    # Generate YAML from .py source code that is using valohai-utils
    source_path = os.path.join(get_project().directory, 'mysnake.py')
    with open(source_path, 'w') as python_fp:
        python_fp.write(PYTHON_SOURCE_USING_VALOHAI_UTILS)
    args = ([source_path])
    rv = runner.invoke(step, args, catch_exceptions=False)
    assert "valohai.yaml generated." in rv.output

    # Update existing YAML from source code
    config_path = os.path.join(get_project().directory, 'valohai.yaml')
    with open(config_path, 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    args = ([source_path])
    rv = runner.invoke(step, args, catch_exceptions=False)
    assert "valohai.yaml updated." in rv.output

    # Try the same update again
    rv = runner.invoke(step, args, catch_exceptions=False)
    assert "valohai.yaml already up-to-date." in rv.output
