import json
import os
import pathlib
import shutil
import subprocess
import time
from dataclasses import dataclass
from itertools import count
from typing import Generator, Iterable, Iterator, Optional, Tuple

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.exceptions import CLIException
from valohai_cli.settings import get_settings_file_name
from valohai_cli.utils import call_with_retry
from valohai_cli.utils.cli_utils import prompt_from_list


@dataclass(frozen=True)
class Keypair:
    public_path: pathlib.Path
    private_path: pathlib.Path


def make_ssh_connection(address: str, port: int, private_key_path: str) -> None:
    ssh_path = shutil.which("ssh")
    if ssh_path is None:
        raise FileNotFoundError(
            "SSH command not found. Ensure SSH is installed and available in your PATH.",
        )
    ssh_command = [
        ssh_path,
        "-i",
        private_key_path,
        f"root@{address}",
        "-p",
        str(port),
        "-t",
        "/bin/bash",
    ]
    subprocess.run(ssh_command)


def find_ssh_details(events: Iterable) -> Optional[Tuple[str, int]]:
    prefix = "::ssh::"
    for event in events:
        if event["message"].startswith(prefix):
            data = json.loads(event["message"][len(prefix) :])
            return data["address"], int(data["port"])
    return None


def get_ssh_key_pairs_from_dir(dir: str) -> Iterator[Keypair]:
    folder_path = pathlib.Path(dir)
    for pth in folder_path.glob("*.pub"):
        if not pth.is_file():
            continue
        try:
            with pth.open("rb") as f:
                first_line = f.readline().strip()
                if first_line.startswith((b"ssh-rsa", b"ecdsa-sha2-", b"ssh-ed25519")):
                    private_key_paths = [pth.with_suffix(""), pth.with_suffix(".pem")]
                    for private_key_path in private_key_paths:
                        if private_key_path.is_file():
                            yield Keypair(public_path=pth, private_path=private_key_path)
                            break
        except OSError:  # e.g. unreadable key
            pass


def select_private_key_from_possible_directories() -> str:
    default_ssh_dir = os.path.expanduser("~/.ssh")
    cli_config_dir = get_settings_file_name("")
    all_keypairs: list[Keypair] = []
    all_dirs = [cli_config_dir, default_ssh_dir]
    for dir in all_dirs:
        if not os.path.isdir(dir):
            continue
        all_keypairs.extend(get_ssh_key_pairs_from_dir(dir))

    if not all_keypairs:
        raise click.UsageError(
            f"No SSH key pairs found in {', '.join(all_dirs)}. Please try to generate new SSH key pair",
        )

    keypair_options = [
        {
            "name": keypair.private_path,
            "description": f"Public: {keypair.public_path}",
        }
        for keypair in all_keypairs
    ]

    selected_key = prompt_from_list(prompt="Select the SSH key pair you want to use", options=keypair_options)
    return str(selected_key["name"])


def fetch_status_events(execution: dict, first_n: Optional[int] = None) -> Generator:
    params = {}
    if first_n is not None:
        params["limit"] = first_n
    events_response = request("get", f"{execution['url']}status-events/", params=params).json()
    yield from events_response.get("status_events", [])


def get_ssh_details_from_execution(execution: dict) -> Tuple[str, int]:
    events_response = fetch_status_events(execution, first_n=100)
    ssh_details = find_ssh_details(events_response)
    if not ssh_details:
        raise click.UsageError("No SSH details found")
    return ssh_details


def get_ssh_details_with_retry(
    counter: int,
) -> Tuple[str, int]:
    """
    Fetch SSH details for a given counter, retrying until the execution has started.

    :param counter: The execution counter.
    :return: A tuple of (IP address, port) for the SSH connection.
    """
    project = get_project(require=True)
    assert project
    for attempt in count():
        execution = project.get_execution_from_counter(
            counter=counter,
            params={"exclude": "metadata, events"},
        )
        if execution["status"] in ("queued", "created"):
            if attempt % 3 == 0:  # print on first attempt and thereafter every 3 attempts
                click.echo(f"Execution #{counter} is {execution['status']}. Waiting for it to start...")
            time.sleep(5)
            continue
        if execution["status"] != "started":
            raise CLIException(f"Execution #{counter} is {execution['status']}. Cannot SSH into it.")
        break
    return call_with_retry(
        func=lambda: get_ssh_details_from_execution(execution=execution),
        retries=5,
        delay_range=(1, 7),
    )
