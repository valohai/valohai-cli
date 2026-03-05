from tests.commands.model.conftest import VERSION_1, VERSION_2, mock_model_api
from valohai_cli.commands.model.versions import versions


def test_versions_list(runner, logged_in, mock_api):
    mock_model_api(mock_api, versions=[VERSION_1, VERSION_2])
    result = runner.invoke(versions, ["sentiment"])
    assert result.exit_code == 0
    assert "Train v1" in result.output
    assert "model-data-v1" in result.output
    assert "model-data-v2" in result.output


def test_versions_empty(runner, logged_in, mock_api):
    mock_model_api(mock_api, versions=[])
    result = runner.invoke(versions, ["sentiment"])
    assert result.exit_code == 0
    assert "No matching versions" in result.output
