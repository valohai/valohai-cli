from tests.commands.model.conftest import MODEL_DATA, MODEL_ID, VERSION_1, mock_model_api
from valohai_cli.commands.model.info import info

INFO_MODEL = {
    **MODEL_DATA,
    "tags": ["production", "nlp"],
    "associated_projects": [{"name": "my-nlp-project"}],
}


def test_model_info_by_id(runner, logged_in, mock_api):
    mock_model_api(mock_api, model=INFO_MODEL, versions=[VERSION_1])
    result = runner.invoke(info, [MODEL_ID])
    assert result.exit_code == 0
    assert "sentiment-bert" in result.output
    assert "acme-corp" in result.output
    assert "alice" in result.output
    assert "Train v1" in result.output
    assert "model-data-v1" in result.output


def test_model_info_by_name(runner, logged_in, mock_api):
    mock_model_api(mock_api, model=INFO_MODEL, versions=[VERSION_1])
    result = runner.invoke(info, ["sentiment"])
    assert result.exit_code == 0
    assert "sentiment-bert" in result.output
