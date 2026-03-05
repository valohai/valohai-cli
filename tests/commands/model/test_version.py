import requests_mock

from valohai_cli.commands.model.version import version

MODEL_DATA = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "name": "sentiment-bert",
    "slug": "sentiment-bert",
    "owner": {"id": 1, "username": "acme-corp"},
    "creator": {"id": 2, "username": "alice"},
    "ctime": "2025-01-10T10:00:00Z",
    "mtime": "2025-02-15T12:00:00Z",
    "access_mode": "organization",
    "tags": [],
    "version_summary": [],
    "descriptions": [],
    "url": "https://app.valohai.com/api/v0/models/aaaaaaaa/",
    "n_comments": 0,
    "associated_project_ids": [],
    "associated_projects": [],
}

VERSION_DETAIL = {
    "id": "vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvv1",
    "model": {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "name": "sentiment-bert",
        "slug": "sentiment-bert",
    },
    "counter": 1,
    "status": "Approved",
    "source": {"type": "execution", "id": "cccccccc-cccc-cccc-cccc-cccccccccccc", "title": "Train v1"},
    "ctime": "2025-01-10T11:00:00Z",
    "mtime": "2025-01-10T11:00:00Z",
    "creator": {"id": 2, "username": "alice"},
    "execution_count": 1,
    "dataset_aliases": [],
    "dataset_version": {
        "name": "model-data-v1",
        "id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
        "ctime": "2025-01-10T10:00:00Z",
    },
    "tags": ["v1"],
    "notes": [],
    "descriptions": [],
}

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


def _mock_apis(m):
    m.get("https://app.valohai.com/api/v0/models/", json={"results": [MODEL_DATA]})
    m.get(
        "https://app.valohai.com/api/v0/models/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
        json=MODEL_DATA,
    )
    m.get("https://app.valohai.com/api/v0/model-versions/", json={"results": [VERSION_DETAIL]})
    m.get(
        "https://app.valohai.com/api/v0/model-versions/vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvv1/source-executions/",
        json={"results": SOURCE_EXECUTIONS},
    )
    m.get(
        "https://app.valohai.com/api/v0/model-versions/vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvv1/source-data/",
        json={"results": SOURCE_DATA},
    )


def test_version_by_counter(runner, logged_in):
    with requests_mock.mock() as m:
        _mock_apis(m)
        result = runner.invoke(version, ["sentiment", "1"])
        assert result.exit_code == 0
        assert "Train v1" in result.output
        assert "model-data-v1" in result.output
        assert "model.pt" in result.output
        assert "train-model" in result.output


def test_version_describe_mode(runner, logged_in):
    with requests_mock.mock() as m:
        _mock_apis(m)
        result = runner.invoke(version, ["sentiment", "1", "--describe"])
        assert result.exit_code == 0
        output = result.output
        assert "# Model Version: sentiment-bert #1" in output
        assert "`vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvv1`" in output
        assert "Approved" in output
        assert "Train v1" in output
        assert "model-data-v1" in output
        assert "| 42 | complete | train-model |" in output
        assert "| model.pt |" in output
