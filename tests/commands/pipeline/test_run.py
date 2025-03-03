from click import BadParameter
from pytest import raises

from tests.commands.run_test_utils import RunAPIMock
from tests.fixture_data import PIPELINE_YAML
from valohai_cli.commands.pipeline.run import run
from valohai_cli.commands.pipeline.run.utils import match_pipeline
from valohai_cli.ctx import get_project


def test_pipeline_run_success(runner, logged_in_and_linked, using_default_run_api_mock):
    add_valid_pipeline_yaml()
    args = ["training"]
    output = runner.invoke(run, args).output

    assert "Success" in output
    assert "Pipeline =21 queued" in output


def test_pipeline_adhoc_run_success(runner, logged_in_and_linked, using_default_run_api_mock):
    add_valid_pipeline_yaml()
    args = ["--adhoc", "training"]
    output = runner.invoke(run, args).output

    assert "Success" in output
    assert "Uploaded ad-hoc code" in output
    assert "Pipeline =21 queued" in output


def test_pipeline_adhoc_with_yaml_path_run_success(runner, logged_in_and_linked, using_default_run_api_mock):
    add_valid_pipeline_yaml(yaml_path="bark.yaml")
    args = ["--adhoc", "--yaml=bark.yaml", "training"]
    output = runner.invoke(run, args).output

    assert "Success" in output
    assert "Uploaded ad-hoc code" in output
    assert "Pipeline =21 queued" in output


def test_pipeline_run_no_name(runner, logged_in_and_linked, using_default_run_api_mock):
    add_valid_pipeline_yaml()
    args = [""]
    output = runner.invoke(run, args).output
    assert "Usage: " in output


def test_match_pipeline(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    config = get_project().get_config()
    matches = match_pipeline(config, "Training")
    assert matches == "Training Pipeline"


def test_match_pipeline_ambiguous(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    config = get_project().get_config()
    with raises(BadParameter):
        match_pipeline(config, "Train")


def add_valid_pipeline_yaml(yaml_path=None):
    project = get_project()
    config_filename = project.get_config_filename(yaml_path=yaml_path)
    with open(config_filename, "w") as yaml_fp:
        yaml_fp.write(PIPELINE_YAML)


def test_pipeline_parameters_overriding_unknown(runner, logged_in_and_linked, using_default_run_api_mock):
    add_valid_pipeline_yaml()
    # Test if it lets unknown pipeline parameters pass through
    overriding_value = "123"
    args = ["--adhoc", "Train Pipeline", "--not-known", overriding_value]
    output = runner.invoke(run, args).output
    assert "Unknown pipeline parameters: ['not-known']" in output


def test_pipeline_parameters_overriding(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    overriding_value = "123"
    args = [
        "--adhoc",
        "Train Pipeline",
        "--pipeline_max_steps",
        overriding_value,
        "--sources+=laituri",
        "--sources+=satama",
    ]
    with RunAPIMock(num_pipeline_parameters=2) as mock_api:
        output = runner.invoke(run, args).output

        # Test that it runs successfully
        assert "Success" in output
        assert "Uploaded ad-hoc code" in output
        assert "Pipeline =21 queued" in output

        # Test that the pipeline parameters were overridden

        max_steps = mock_api.last_create_pipeline_payload["parameters"]["pipeline_max_steps"]
        assert max_steps["expression"] == overriding_value
        sources = mock_api.last_create_pipeline_payload["parameters"]["sources"]
        assert sources["expression"] == {
            "style": "single",
            # Use local sources
            "rules": {
                "value": ["laituri", "satama"],
            },
        }
