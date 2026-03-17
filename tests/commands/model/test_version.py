from tests.commands.model.conftest import VERSION_1, VERSION_ID_1, mock_model_api
from valohai_cli.commands.model.version import version

SOURCE_EXECUTIONS = [
    {
        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "counter": 42,
        "status": "complete",
        "step": "train-model",
        "ctime": "2025-01-10T10:30:00Z",
    },
]

SOURCE_DATA = [
    {
        "id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
        "name": "model.pt",
        "size": 1048576,
        "ctime": "2025-01-10T10:45:00Z",
    },
]


def _mock_version_sub_apis(m):
    m.get(
        f"https://app.valohai.com/api/v0/model-versions/{VERSION_ID_1}/source-executions/",
        json={"results": SOURCE_EXECUTIONS},
    )
    m.get(
        f"https://app.valohai.com/api/v0/model-versions/{VERSION_ID_1}/source-data/",
        json={"results": SOURCE_DATA},
    )


def test_version_by_counter(runner, logged_in, mock_api):
    mock_model_api(mock_api, versions=[VERSION_1])
    _mock_version_sub_apis(mock_api)
    result = runner.invoke(version, ["sentiment", "1"])
    assert result.exit_code == 0
    assert "Train v1" in result.output
    assert "model-data-v1" in result.output
    assert "model.pt" in result.output
    assert "train-model" in result.output


def test_version_describe_mode(runner, logged_in, mock_api):
    mock_model_api(mock_api, versions=[VERSION_1])
    _mock_version_sub_apis(mock_api)
    result = runner.invoke(version, ["sentiment", "1", "--describe"])
    assert result.exit_code == 0
    output = result.output
    assert "# Model Version: sentiment-bert #1" in output
    assert f"`{VERSION_ID_1}`" in output
    assert "Approved" in output
    assert "Train v1" in output
    assert "model-data-v1" in output
    assert "| 42 | complete | train-model |" in output
    assert "| model.pt |" in output
