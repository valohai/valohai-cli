import requests_mock

from valohai_cli.commands.model.list import list

MODEL_LIST_DATA = [
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "name": "sentiment-bert",
        "slug": "sentiment-bert",
        "owner": {"id": 1, "username": "acme-corp"},
        "creator": {"id": 2, "username": "alice"},
        "ctime": "2025-01-10T10:00:00Z",
        "mtime": "2025-02-15T12:00:00Z",
        "access_mode": "organization",
        "tags": ["production", "nlp"],
        "version_summary": [
            {"counter": 1, "status": "Approved"},
            {"counter": 2, "status": "Pending"},
        ],
        "descriptions": {},
        "url": "https://app.valohai.com/api/v0/models/aaaaaaaa/",
        "n_comments": 0,
        "associated_project_ids": [],
        "associated_projects": [],
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "name": "image-classifier",
        "slug": "image-classifier",
        "owner": {"id": 1, "username": "acme-corp"},
        "creator": {"id": 3, "username": "bob"},
        "ctime": "2025-03-01T08:00:00Z",
        "mtime": "2025-03-01T09:00:00Z",
        "access_mode": "organization",
        "tags": [],
        "version_summary": [],
        "descriptions": {},
        "url": "https://app.valohai.com/api/v0/models/bbbbbbbb/",
        "n_comments": 0,
        "associated_project_ids": [],
        "associated_projects": [],
    },
]


def test_model_list(runner, logged_in):
    with requests_mock.mock() as m:
        m.get(
            "https://app.valohai.com/api/v0/models/",
            json={"results": MODEL_LIST_DATA},
        )
        result = runner.invoke(list)
        assert result.exit_code == 0
        assert "sentiment-bert" in result.output
        assert "image-classifier" in result.output
        assert "acme-corp" in result.output


def test_model_list_quiet(runner, logged_in):
    with requests_mock.mock() as m:
        m.get(
            "https://app.valohai.com/api/v0/models/",
            json={"results": MODEL_LIST_DATA},
        )
        result = runner.invoke(list, ["--quiet"])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        assert len(lines) == 2
        assert "sentiment-bert\taaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" in lines[0]
        assert "image-classifier\tbbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb" in lines[1]


def test_model_list_empty(runner, logged_in):
    with requests_mock.mock() as m:
        m.get(
            "https://app.valohai.com/api/v0/models/",
            json={"results": []},
        )
        result = runner.invoke(list)
        assert result.exit_code == 0
        assert "No models found" in result.output
