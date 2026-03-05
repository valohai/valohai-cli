from tests.commands.model.conftest import MODEL_DATA, MODEL_ID, MODEL_ID_2
from valohai_cli.commands.model.list import list

MODEL_LIST_DATA = [
    {
        **MODEL_DATA,
        "tags": ["production", "nlp"],
        "version_summary": [
            {"counter": 1, "status": "Approved"},
            {"counter": 2, "status": "Pending"},
        ],
    },
    {
        **MODEL_DATA,
        "id": MODEL_ID_2,
        "name": "image-classifier",
        "slug": "image-classifier",
        "creator": {"id": 3, "username": "bob"},
        "ctime": "2025-03-01T08:00:00Z",
        "mtime": "2025-03-01T09:00:00Z",
        "tags": [],
        "version_summary": [],
    },
]


def test_model_list(runner, logged_in, mock_api):
    mock_api.get("https://app.valohai.com/api/v0/models/", json={"results": MODEL_LIST_DATA})
    result = runner.invoke(list)
    assert result.exit_code == 0
    assert "sentiment-bert" in result.output
    assert "image-classifier" in result.output
    assert "acme-corp" in result.output


def test_model_list_quiet(runner, logged_in, mock_api):
    mock_api.get("https://app.valohai.com/api/v0/models/", json={"results": MODEL_LIST_DATA})
    result = runner.invoke(list, ["--quiet"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert len(lines) == 2
    assert f"sentiment-bert\t{MODEL_ID}" in lines[0]
    assert f"image-classifier\t{MODEL_ID_2}" in lines[1]


def test_model_list_empty(runner, logged_in, mock_api):
    mock_api.get("https://app.valohai.com/api/v0/models/", json={"results": []})
    result = runner.invoke(list)
    assert result.exit_code == 0
    assert "No models found" in result.output
