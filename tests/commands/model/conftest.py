import pytest
import requests_mock

MODEL_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
MODEL_ID_2 = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
VERSION_ID_1 = "vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvv1"
VERSION_ID_2 = "vvvvvvvv-vvvv-vvvv-vvvv-vvvvvvvvvvv2"

MODEL_DATA = {
    "id": MODEL_ID,
    "name": "sentiment-bert",
    "slug": "sentiment-bert",
    "owner": {"id": 1, "username": "acme-corp"},
    "creator": {"id": 2, "username": "alice"},
    "ctime": "2025-01-10T10:00:00Z",
    "mtime": "2025-02-15T12:00:00Z",
    "access_mode": "organization",
    "tags": [],
    "archived": False,
    "version_summary": [],
    "descriptions": [],
    "url": f"https://app.valohai.com/api/v0/models/{MODEL_ID}/",
    "n_comments": 0,
    "associated_project_ids": [],
    "associated_projects": [],
    "teams": [],
}

VERSION_1 = {
    "id": VERSION_ID_1,
    "model": {"id": MODEL_ID, "name": "sentiment-bert", "slug": "sentiment-bert"},
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

VERSION_2 = {
    "id": VERSION_ID_2,
    "model": {"id": MODEL_ID, "name": "sentiment-bert", "slug": "sentiment-bert"},
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
}


def mock_model_api(
    mocker: requests_mock.Mocker,
    model: dict = MODEL_DATA,
    versions: list | None = None,
) -> None:
    """Register mock responses for model detail, list, and optionally versions."""
    mocker.get(f"https://app.valohai.com/api/v0/models/{model['id']}/", json=model)
    mocker.get("https://app.valohai.com/api/v0/models/", json={"results": [model]})
    if versions is not None:
        mocker.get("https://app.valohai.com/api/v0/model-versions/", json={"results": versions})


@pytest.fixture
def mock_api():
    with requests_mock.Mocker() as mocker:
        yield mocker
