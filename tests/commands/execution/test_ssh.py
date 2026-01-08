import shutil
import subprocess
import time

from tests.commands.execution.utils import get_execution_data_mock, no_sleep
from tests.fixtures.data import EXECUTION_DETAIL_DATA, STATUS_EVENT_RESPONSE_DATA
from valohai_cli.commands.execution.ssh import ssh


def test_ssh_in_completed_execution(runner, logged_in_and_linked, monkeypatch):
    with get_execution_data_mock():
        counter = EXECUTION_DETAIL_DATA["counter"]
        result = runner.invoke(ssh, [str(counter)], catch_exceptions=False)
        assert f"Error: Execution #{counter} is complete. Cannot SSH into it.\n" in result.output
        assert result.exit_code == 1


def test_ssh_in_queued_execution(runner, logged_in_and_linked, monkeypatch):
    counter = EXECUTION_DETAIL_DATA["counter"]
    monkeypatch.setitem(EXECUTION_DETAIL_DATA, "status", "queued")
    monkeypatch.setattr(time, "sleep", no_sleep)
    with get_execution_data_mock():
        result = runner.invoke(ssh, [str(counter)], catch_exceptions=False)
        assert f"Execution #{counter} is queued. Waiting for it to start...\n" in result.output
        assert result.exit_code == 1


def test_ssh_with_no_ssh_details_present(runner, logged_in_and_linked, monkeypatch):
    counter = EXECUTION_DETAIL_DATA["counter"]
    monkeypatch.setitem(EXECUTION_DETAIL_DATA, "status", "started")
    monkeypatch.setattr(time, "sleep", lambda x: None)
    with get_execution_data_mock() as m:
        m.get(
            f"https://app.valohai.com/api/v0/executions/{EXECUTION_DETAIL_DATA['id']}/status-events/",
            json={"status_events": []},
        )
        result = runner.invoke(ssh, [str(counter)], catch_exceptions=False)
        output = result.output
        assert "1/5 Retrying: No SSH details found...\n" in output
        assert "2/5 Retrying: No SSH details found...\n" in output
        assert "3/5 Retrying: No SSH details found...\n" in output
        assert "4/5 Retrying: No SSH details found...\n" in output
        assert "5/5 Retrying: No SSH details found...\n" in output

    assert result.exit_code == 1


def test_ssh(runner, logged_in_and_linked, monkeypatch, tmp_path):
    counter = EXECUTION_DETAIL_DATA["counter"]
    monkeypatch.setitem(EXECUTION_DETAIL_DATA, "status", "started")

    def mock_prompt():
        return tmp_path

    monkeypatch.setattr(
        "valohai_cli.commands.execution.ssh.select_private_key_from_possible_directories",
        mock_prompt,
    )

    with get_execution_data_mock() as m:
        m.get(
            f"https://app.valohai.com/api/v0/executions/{EXECUTION_DETAIL_DATA['id']}/status-events/",
            json=STATUS_EVENT_RESPONSE_DATA,
        )
        result = runner.invoke(ssh, [str(counter)], catch_exceptions=False)
        output = result.output
        assert "SSH address is 127.0.0.1:2222" in output

        def mock_subprocess_run(*args, **kwargs):
            print(args[0])
            return subprocess.CompletedProcess(args=args, returncode=0)

        monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

        result = result.runner.invoke(ssh, [str(counter)], input="1", catch_exceptions=False)
        assert (
            f"['{shutil.which('ssh')}', '-i', PosixPath('{tmp_path}'), 'root@127.0.0.1', '-p', '2222', '-t', '/bin/bash']"
            in result.output
        )
        assert result.exit_code == 0
