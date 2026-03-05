import requests_mock

from valohai_cli.commands.model.info import info

MODEL_DETAIL_DATA = {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "name": "sentiment-bert",
    "slug": "sentiment-bert",
    "owner": {"id": 1, "username": "acme-corp"},
    "creator": {"id": 2, "username": "alice"},
    "ctime": "2025-01-10T10:00:00Z",
    "mtime": "2025-02-15T12:00:00Z",
    "access_mode": "organization",
    "tags": ["production", "nlp"],
    "version_summary": [],
    "descriptions": {},
    "url": "https://app.valohai.com/api/v0/models/aaaaaaaa/",
    "n_comments": 0,
    "associated_project_ids": [],
    "associated_projects": [{"name": "my-nlp-project"}],
    "teams": [],
}

MODEL_VERSION_DATA = {
    "id": "vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvvv",
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


def _mock_model_apis(m):
    m.get(
        "https://app.valohai.com/api/v0/models/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
        json=MODEL_DETAIL_DATA,
    )
    m.get(
        "https://app.valohai.com/api/v0/models/",
        json={"results": [MODEL_DETAIL_DATA]},
    )
    m.get(
        "https://app.valohai.com/api/v0/model-versions/",
        json={"results": [MODEL_VERSION_DATA]},
    )


def test_model_info_by_id(runner, logged_in):
    with requests_mock.mock() as m:
        _mock_model_apis(m)
        result = runner.invoke(info, ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"])
        assert result.exit_code == 0
        assert "sentiment-bert" in result.output
        assert "acme-corp" in result.output
        assert "alice" in result.output
        assert "Train v1" in result.output
        assert "model-data-v1" in result.output


def test_model_info_by_name(runner, logged_in):
    with requests_mock.mock() as m:
        _mock_model_apis(m)
        result = runner.invoke(info, ["sentiment"])
        assert result.exit_code == 0
        assert "sentiment-bert" in result.output
