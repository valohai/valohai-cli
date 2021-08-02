import os

from tests.fixture_data import (
    PYTHON_SOURCE,
    PYTHON_SOURCE_DEFINING_PIPELINE,
    YAML_WITH_EXTRACT_TRAIN_EVAL,
    YAML_WITH_TRAIN_EVAL,
)
from valohai_cli.commands.yaml.pipeline import pipeline
from valohai_cli.ctx import get_project


def test_pipeline(runner, logged_in_and_linked):
    # Create config with only two steps
    config_path = os.path.join(get_project().directory, 'valohai.yaml')
    with open(config_path, 'w') as yaml_fp:
        yaml_fp.write(YAML_WITH_TRAIN_EVAL)

    # Try to generate pipeline from random .py source code.
    source_path = os.path.join(get_project().directory, 'random.py')
    with open(source_path, 'w') as python_fp:
        python_fp.write(PYTHON_SOURCE)
    args = ([source_path])
    rv = runner.invoke(pipeline, args, catch_exceptions=True)
    # The .py source was random so we should get an error
    assert isinstance(rv.exception, AttributeError)

    # Try generating pipeline from .py source code that is correctly using valohai-utils & papi
    source_path = os.path.join(get_project().directory, 'mysnake.py')
    with open(source_path, 'w') as python_fp:
        python_fp.write(PYTHON_SOURCE_DEFINING_PIPELINE)
    args = ([source_path])
    rv = runner.invoke(pipeline, args, catch_exceptions=True)
    # The current config is missing one of the three steps on purpose. This should raise an exception.
    assert isinstance(rv.exception, ValueError)

    # Now re-create config with all the three steps
    config_path = os.path.join(get_project().directory, 'valohai.yaml')
    with open(config_path, 'w') as yaml_fp:
        yaml_fp.write(YAML_WITH_EXTRACT_TRAIN_EVAL)

    # With all the three steps, we are expecting great success
    args = ([source_path])
    rv = runner.invoke(pipeline, args, catch_exceptions=False)
    assert "valohai.yaml updated." in rv.output

    # Try the same update again
    rv = runner.invoke(pipeline, args, catch_exceptions=False)
    assert "valohai.yaml already up-to-date." in rv.output
