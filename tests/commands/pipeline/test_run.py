from click import BadParameter
from pytest import raises

from tests.commands.run_test_utils import RunAPIMock
from tests.fixture_data import PIPELINE_YAML, PROJECT_DATA
from valohai_cli.commands.pipeline.run import run
from valohai_cli.commands.pipeline.run.utils import match_pipeline
from valohai_cli.ctx import get_project


def test_pipeline_run_success(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = ['training']
    with RunAPIMock(PROJECT_DATA['id']):
        output = runner.invoke(run, args).output
    assert 'Success' in output


def test_pipeline_adhoc_run_success(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = ['--adhoc', 'training']
    with RunAPIMock(PROJECT_DATA['id']):
        print(run, args)
        output = runner.invoke(run, args).output
    assert 'Success' in output
    assert 'Uploaded ad-hoc code' in output


def test_pipeline_adhoc_with_yaml_path_run_success(runner, logged_in_and_linked):
    add_valid_pipeline_yaml(yaml_path='bark.yaml')
    args = ['--adhoc', '--yaml=bark.yaml', 'training']
    with RunAPIMock(PROJECT_DATA['id']):
        output = runner.invoke(run, args).output
    assert 'Success' in output
    assert 'Uploaded ad-hoc code' in output


def test_pipeline_run_no_name(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = ['']
    with RunAPIMock(PROJECT_DATA['id']):
        output = runner.invoke(run, args).output
    assert 'Usage: ' in output


def test_match_pipeline(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    config = get_project().get_config()
    matches = match_pipeline(config, 'Training')
    assert matches == "Training Pipeline"


def test_match_pipeline_ambiguous(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    config = get_project().get_config()
    with raises(BadParameter):
        match_pipeline(config, 'Train')


def add_valid_pipeline_yaml(yaml_path=None):
    project = get_project()
    config_filename = project.get_config_filename(yaml_path=yaml_path)
    with open(config_filename, 'w') as yaml_fp:
        yaml_fp.write(PIPELINE_YAML)
