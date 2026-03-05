import requests_mock

from valohai_cli.commands.model.versions import versions

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

VERSION_DATA = [
    {
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
    },
    {
        "id": "vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvv2",
        "model": {
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "name": "sentiment-bert",
            "slug": "sentiment-bert",
        },
        "counter": 2,
        "status": "Pending",
        "source": {"type": "manual", "id": None, "title": None},
        "ctime": "2025-02-15T12:00:00Z",
        "mtime": "2025-02-15T12:00:00Z",
        "creator": {"id": 2, "username": "alice"},
        "execution_count": 0,
        "dataset_aliases": [],
        "dataset_version": {
            "name": "model-data-v2",
            "id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "ctime": "2025-02-15T11:00:00Z",
        },
        "tags": [],
        "notes": [],
        "descriptions": [],
    },
]


def _mock_apis(m):
    m.get(
        "https://app.valohai.com/api/v0/models/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
        json=MODEL_DATA,
    )
    m.get(
        "https://app.valohai.com/api/v0/models/",
        json={"results": [MODEL_DATA]},
    )
    m.get(
        "https://app.valohai.com/api/v0/model-versions/",
        json={"results": VERSION_DATA},
    )


def test_versions_list(runner, logged_in):
    with requests_mock.mock() as m:
        _mock_apis(m)
        result = runner.invoke(versions, ["sentiment"])
        assert result.exit_code == 0
        assert "Train v1" in result.output
        assert "model-data-v1" in result.output
        assert "model-data-v2" in result.output


def test_versions_empty(runner, logged_in):
    with requests_mock.mock() as m:
        m.get("https://app.valohai.com/api/v0/models/", json={"results": [MODEL_DATA]})
        m.get(
            "https://app.valohai.com/api/v0/models/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
            json=MODEL_DATA,
        )
        m.get("https://app.valohai.com/api/v0/model-versions/", json={"results": []})
        result = runner.invoke(versions, ["sentiment"])
        assert result.exit_code == 0
        assert "No matching versions" in result.output
