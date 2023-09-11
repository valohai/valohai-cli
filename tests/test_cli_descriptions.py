from __future__ import annotations

import json
import sys
from typing import Any

import pytest

from valohai_cli.cli import cli
from valohai_cli.consts import json_help_envvar


def find_commands_with_no_help(
    command: dict[str, Any],
    trail: tuple[dict[str, Any], ...] = (),
):
    command_with_trail = (*trail, command)
    full_command_name = " ".join([c["name"] for c in command_with_trail])
    if not (
        full_command_name == "vh" or command.get("hidden") or command.get("deprecated")
    ):
        help_text = (command.get("short_help") or command.get("help") or "").strip()
        if not help_text:
            yield NotImplementedError(f"Command {full_command_name!r} has no help text")
    for subcommand in command.get("commands", {}).values():
        yield from find_commands_with_no_help(subcommand, command_with_trail)


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="requires python3.11 or higher",  # (ExceptionGroup)
)
def test_all_commands_have_help(runner, monkeypatch):
    monkeypatch.setenv(json_help_envvar, "1")
    root_command = json.loads(runner.invoke(cli, ["--help"]).output)["command"]
    assert root_command["name"] == "cli"
    root_command["name"] = "vh"  # for easier reading
    exceptions = list(find_commands_with_no_help(root_command))

    if exceptions:
        raise ExceptionGroup(
            f"{len(exceptions)} commands have no help text", exceptions
        )
