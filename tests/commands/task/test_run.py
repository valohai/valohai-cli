from __future__ import annotations

import pytest
from click.testing import CliRunner

from tests.commands.run_test_utils import RunAPIMock
from tests.fixtures.config import TASK_YAML
from tests.fixtures.data import PROJECT_DATA, TASK_DETAIL_DATA
from valohai_cli import git
from valohai_cli.commands.task.run import run
from valohai_cli.ctx import get_project


@pytest.fixture()
def task_run_setup(logged_in_and_linked, monkeypatch):
    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(TASK_YAML)
    project_id = str(PROJECT_DATA["id"])
    commit_id = "f" * 16
    monkeypatch.setattr(git, "get_current_commit", lambda dir: commit_id)
    api_mock = RunAPIMock(project_id, commit_id=commit_id)
    return api_mock


def test_task_run_help(runner, logged_in_and_linked):
    """Test that --help shows available tasks."""
    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(TASK_YAML)
    output = runner.invoke(run, ["--help"]).output
    assert "hyperparameter-sweep" in output
    assert "random-sweep" in output


def test_task_run_basic(task_run_setup):
    """Test basic task creation with default blueprint values."""
    with task_run_setup:
        output = CliRunner().invoke(run, ["hyperparameter-sweep"], catch_exceptions=False).output
        assert f"!{TASK_DETAIL_DATA['counter']}" in output

    payload = task_run_setup.last_create_task_payload
    assert payload["type"] == "grid_search"
    assert payload["step"] == "Train model"
    assert payload["maximum_queued_executions"] == 3
    assert payload["on_child_error"] == "stop_all_and_error"

    # Check variant parameters from the blueprint
    params = payload["parameters"]
    assert params["learning_rate"] == {
        "style": "logspace",
        "rules": {"min": -5, "max": -1, "count": 5},
    }
    assert params["max_steps"] == {
        "style": "multiple",
        "rules": {"items": [100, 200, 300]},
    }


def test_task_run_with_overrides(task_run_setup):
    """Test task creation with CLI overrides."""
    with task_run_setup:
        output = (
            CliRunner()
            .invoke(
                run,
                [
                    "hyperparameter-sweep",
                    "--title=my sweep",
                    "--tag=experiment",
                    "--max-queued=10",
                    "--on-child-error=continue-and-complete",
                    "--environment=some-env-id",
                ],
                catch_exceptions=False,
            )
            .output
        )
        assert f"!{TASK_DETAIL_DATA['counter']}" in output

    payload = task_run_setup.last_create_task_payload
    assert payload["title"] == "my sweep"
    assert payload["tags"] == ["experiment"]
    assert payload["maximum_queued_executions"] == 10
    assert payload["on_child_error"] == "continue_and_complete"
    assert payload["environment"] == "some-env-id"


@pytest.mark.parametrize(
    ("args", "expected_priority"),
    [
        (["--priority=7"], 7),
        (["--priority"], 1),
        ([], None),
    ],
    ids=("explicit", "implicit", "none"),
)
def test_task_run_priority(task_run_setup, args, expected_priority):
    with task_run_setup:
        CliRunner().invoke(run, ["hyperparameter-sweep", *args], catch_exceptions=False)

    payload = task_run_setup.last_create_task_payload
    if expected_priority is None:
        assert "priority" not in payload
    else:
        assert payload["priority"] == expected_priority


def test_task_run_with_input_override(task_run_setup):
    """Test that step inputs can be overridden from CLI."""
    with task_run_setup:
        output = (
            CliRunner()
            .invoke(
                run,
                [
                    "hyperparameter-sweep",
                    "--in1=http://custom-data.example.com/data.csv",
                ],
                catch_exceptions=False,
            )
            .output
        )
        assert f"!{TASK_DETAIL_DATA['counter']}" in output

    payload = task_run_setup.last_create_task_payload
    assert list(payload["inputs"]["in1"]) == ["http://custom-data.example.com/data.csv"]


def test_task_run_random_sweep(task_run_setup):
    """Test creation of a random search task with configuration."""
    with task_run_setup:
        output = CliRunner().invoke(run, ["random-sweep"], catch_exceptions=False).output
        assert f"!{TASK_DETAIL_DATA['counter']}" in output

    payload = task_run_setup.last_create_task_payload
    assert payload["type"] == "random_search"
    assert payload["maximum_queued_executions"] == 5
    assert payload["configuration"] == {"execution_count": 20}


def test_task_run_no_tasks(runner, logged_in_and_linked, patch_git, using_default_run_api_mock):
    """Test that an informative error is shown when no tasks match."""
    from tests.fixtures.config import CONFIG_YAML

    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(CONFIG_YAML)  # No tasks defined
    output = runner.invoke(run, ["nonexistent"]).output
    assert "is not a known task" in output


def test_task_run_step_help(task_run_setup):
    """Test that step-level --help shows parameter/input options."""
    with task_run_setup:
        output = CliRunner().invoke(run, ["hyperparameter-sweep", "--help"]).output
    assert "Parameter Options" in output
    assert "Input Options" in output
    assert "--max-steps" in output
    assert "--in1" in output
