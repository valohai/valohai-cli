import requests_mock

from valohai_cli.commands.model.describe import describe

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
    "archived": False,
    "version_summary": [],
    "descriptions": [
        {
            "title": "Overview",
            "category": "Overview",
            "body": "A BERT model fine-tuned for sentiment analysis.",
        },
    ],
    "url": "https://app.valohai.com/api/v0/models/aaaaaaaa/",
    "n_comments": 0,
    "associated_project_ids": [],
    "associated_projects": [{"name": "my-nlp-project"}],
    "teams": [],
}

MODEL_VERSIONS_DATA = [
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
        "source": {
            "type": "pipeline",
            "id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
            "title": "Retrain pipeline",
        },
        "ctime": "2025-02-15T12:00:00Z",
        "mtime": "2025-02-15T12:00:00Z",
        "creator": {"id": 2, "username": "alice"},
        "execution_count": 3,
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
        json={"results": MODEL_VERSIONS_DATA},
    )


def test_describe_markdown_output(runner, logged_in):
    with requests_mock.mock() as m:
        _mock_model_apis(m)
        result = runner.invoke(describe, ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"])
        assert result.exit_code == 0
        output = result.output
        assert "# Model: sentiment-bert" in output
        assert "`aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa`" in output
        assert "acme-corp" in output
        assert "alice" in output
        assert "`production`" in output
        assert "`nlp`" in output
        assert "A BERT model fine-tuned for sentiment analysis." in output
        assert "my-nlp-project" in output
        # Version table
        assert "| 1 | Approved | Train v1 | v1 | model-data-v1 |" in output
        assert "| 2 | Pending | Retrain pipeline |  | model-data-v2 |" in output


def test_describe_no_versions(runner, logged_in):
    with requests_mock.mock() as m:
        # No need to mock model-versions since --no-versions skips the call
        m.get(
            "https://app.valohai.com/api/v0/models/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
            json=MODEL_DETAIL_DATA,
        )
        m.get(
            "https://app.valohai.com/api/v0/models/",
            json={"results": [MODEL_DETAIL_DATA]},
        )
        result = runner.invoke(describe, ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "--no-versions"])
        assert result.exit_code == 0
        assert "## Versions" not in result.output
        assert "# Model: sentiment-bert" in result.output
