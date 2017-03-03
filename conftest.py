import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def isolate_cli(tmpdir, monkeypatch):
    config_dir = str(tmpdir.mkdir('cfg'))
    project_dir = str(tmpdir.mkdir('proj'))
    monkeypatch.setenv('VALOHAI_CONFIG_DIR', config_dir)
    monkeypatch.setenv('VALOHAI_PROJECT_DIR', project_dir)
