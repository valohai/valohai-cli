from tests.commands.model.conftest import MODEL_DATA, MODEL_ID, VERSION_1, VERSION_2, mock_model_api
from valohai_cli.commands.model.describe import describe

DESCRIBE_MODEL = {
    **MODEL_DATA,
    "tags": ["production", "nlp"],
    "descriptions": [
        {
            "title": "Overview",
            "category": "Overview",
            "body": "A BERT model fine-tuned for sentiment analysis.",
        },
    ],
    "associated_projects": [{"name": "my-nlp-project"}],
}

DESCRIBE_VERSION_2 = {
    **VERSION_2,
    "source": {"type": "pipeline", "id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee", "title": "Retrain pipeline"},
}


def test_describe_markdown_output(runner, logged_in, mock_api):
    mock_model_api(mock_api, model=DESCRIBE_MODEL, versions=[VERSION_1, DESCRIBE_VERSION_2])
    result = runner.invoke(describe, [MODEL_ID])
    assert result.exit_code == 0
    output = result.output
    assert "# Model: sentiment-bert" in output
    assert f"`{MODEL_ID}`" in output
    assert "acme-corp" in output
    assert "alice" in output
    assert "`production`" in output
    assert "`nlp`" in output
    assert "A BERT model fine-tuned for sentiment analysis." in output
    assert "my-nlp-project" in output
    assert "| 1 | Approved | Train v1 | v1 | model-data-v1 |" in output
    assert "| 2 | Pending | Retrain pipeline |  | model-data-v2 |" in output


def test_describe_no_versions(runner, logged_in, mock_api):
    mock_model_api(mock_api, model=DESCRIBE_MODEL)
    result = runner.invoke(describe, [MODEL_ID, "--no-versions"])
    assert result.exit_code == 0
    assert "## Versions" not in result.output
    assert "# Model: sentiment-bert" in result.output
