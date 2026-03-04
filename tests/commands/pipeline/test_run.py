from click import BadParameter
from pytest import raises

from tests.commands.run_test_utils import RunAPIMock
from tests.fixtures.config import PIPELINE_WITH_TASK_EXAMPLE, PIPELINE_YAML
from tests.fixtures.data import PROJECT_DATA
from tests.utils import write_yaml_config
from valohai_cli.commands.pipeline.run import run
from valohai_cli.commands.pipeline.run.run import process_args
from valohai_cli.commands.pipeline.run.utils import match_pipeline
from valohai_cli.ctx import get_project


def test_pipeline_run_success(runner, logged_in_and_linked, using_default_run_api_mock, patch_git):
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


def add_valid_pipeline_yaml(yaml_path=None) -> None:
    write_yaml_config(PIPELINE_YAML, yaml_path=yaml_path)


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


def test_pipeline_environment_override(runner, logged_in_and_linked):
    write_yaml_config(PIPELINE_WITH_TASK_EXAMPLE)
    args = ["--adhoc", "--environment=tiny", "dynamic-task"]
    with RunAPIMock(
        PROJECT_DATA["id"],
        expected_edge_count=3,
        expected_node_count=4,
        num_pipeline_parameters=0,
    ) as mock_api:
        output = runner.invoke(run, args).output
        print(output)
        assert "Success" in output
        for node in mock_api.last_create_pipeline_payload["nodes"]:
            if node["type"] in ("execution", "task"):
                assert node["template"]["environment"] == "tiny"


def test_pipeline_node_parameter_override(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = [
        "--adhoc",
        "Train Pipeline",
        "--train.max_steps=500",
    ]
    with RunAPIMock(num_pipeline_parameters=2) as mock_api:
        output = runner.invoke(run, args).output
        assert "Success" in output

        nodes = mock_api.last_create_pipeline_payload["nodes"]
        train_node = next(node for node in nodes if node["name"] == "train")
        assert train_node["template"]["parameters"]["max_steps"] == "500"


def test_pipeline_node_input_override(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = [
        "--adhoc",
        "Train Pipeline",
        "--train.training-set-images=https://example.com/custom-images.gz",
    ]
    with RunAPIMock(num_pipeline_parameters=2) as mock_api:
        output = runner.invoke(run, args).output
        assert "Success" in output

        nodes = mock_api.last_create_pipeline_payload["nodes"]
        train_node = next(node for node in nodes if node["name"] == "train")
        assert (
            train_node["template"]["inputs"]["training-set-images"] == "https://example.com/custom-images.gz"
        )


def test_pipeline_node_parameter_invalid_node(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = [
        "--adhoc",
        "Train Pipeline",
        "--nonexistent.max_steps=500",
    ]
    with RunAPIMock(num_pipeline_parameters=2):
        output = runner.invoke(run, args).output
        assert "Node 'nonexistent' not found in the pipeline" in output


def test_pipeline_node_parameter_invalid_parameter(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = [
        "--adhoc",
        "Train Pipeline",
        "--train.nonexistent_param=500",
    ]
    with RunAPIMock(num_pipeline_parameters=2):
        output = runner.invoke(run, args).output
        assert "train.nonexistent_param does not refer to a parameter or input" in output


def test_pipeline_node_input_invalid_uri(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = [
        "--adhoc",
        "Train Pipeline",
        "--train.training-set-images=not-a-uri",
    ]
    with RunAPIMock(num_pipeline_parameters=2):
        output = runner.invoke(run, args).output
        assert "must be valid URI" in output


def test_pipeline_mixed_parameters_and_node_overrides(runner, logged_in_and_linked):
    add_valid_pipeline_yaml()
    args = [
        "--adhoc",
        "Train Pipeline",
        "--pipeline_max_steps=800",
        "--train.learning_rate=0.01",
        "--sources+=custom",
    ]
    with RunAPIMock(num_pipeline_parameters=2) as mock_api:
        output = runner.invoke(run, args).output
        assert "Success" in output

        params = mock_api.last_create_pipeline_payload["parameters"]
        nodes = mock_api.last_create_pipeline_payload["nodes"]

        assert params["pipeline_max_steps"]["expression"] == "800"
        assert params["sources"]["expression"] == {
            "style": "single",
            "rules": {
                "value": ["custom"],
            },
        }

        train_node = next(node for node in nodes if node["name"] == "train")
        assert train_node["template"]["parameters"]["learning_rate"] == "0.01"


def test_process_args_parsing():
    # Test basic pipeline parameter
    result = process_args(["--param=value"])
    assert result.pipeline_parameters == {"param": "value"}
    assert result.node_parameters == {}

    # Test node parameter with dot notation
    result = process_args(["--node.param=value"])
    assert result.pipeline_parameters == {}
    assert result.node_parameters == {("node", "param"): "value"}

    # Test mixed parameters
    result = process_args(["--pipeline_param=100", "--node.param=200"])
    assert result.pipeline_parameters == {"pipeline_param": "100"}
    assert result.node_parameters == {("node", "param"): "200"}

    # Test list append syntax for pipeline parameter
    result = process_args(["--sources+=port", "--sources+=dock"])
    assert result.pipeline_parameters == {"sources": ["port", "dock"]}
    assert result.node_parameters == {}

    # Test list append syntax for node parameter
    result = process_args(["--node.sources+=port", "--node.sources+=dock"])
    assert result.pipeline_parameters == {}
    assert result.node_parameters == {("node", "sources"): ["port", "dock"]}

    # Test space-separated values
    result = process_args(["--param", "value"])
    assert result.pipeline_parameters == {"param": "value"}

    result = process_args(["--node.param", "value"])
    assert result.node_parameters == {("node", "param"): "value"}

    # Test flag (no value)
    result = process_args(["--flag"])
    assert result.pipeline_parameters == {"flag": "true"}

    result = process_args(["--node.flag"])
    assert result.node_parameters == {("node", "flag"): "true"}
