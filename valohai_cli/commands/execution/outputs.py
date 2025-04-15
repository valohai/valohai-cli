import os
import time
from fnmatch import fnmatch
from typing import List, Optional

import click
import requests

from valohai_cli.api import get_user_agent, request
from valohai_cli.consts import complete_execution_statuses
from valohai_cli.ctx import get_project
from valohai_cli.messages import info, success, warn
from valohai_cli.table import print_table
from valohai_cli.utils.cli_utils import counter_argument

DOWNLOAD_HELP = (
    "Download files to this directory (by default, don't download). "
    "You can use `{counter}` as a placeholder that will be replaced by the execution's "
    "counter number."
)

GLOB_HELP = (
    "Download only files matching this glob.\n"
    "Be sure to wrap the value in single quotes (or however appropriate for your shell) "
    "to avoid your shell expanding the wildcard, e.g. `outputs -f '*.csv'`."
)


def get_execution_outputs(execution: dict) -> List[dict]:
    return list(
        request(
            method="get",
            url="/api/v0/data/",
            params={
                "output_execution": execution["id"],
                "limit": 9000,
            },
        )
        .json()
        .get("results", []),
    )


@click.command()
@counter_argument
@click.option(
    "--download",
    "-d",
    "download_directory",
    type=click.Path(file_okay=False),
    help=DOWNLOAD_HELP,
    default=None,
)
@click.option(
    "--filter-download",
    "-f",
    help=GLOB_HELP,
    default=None,
)
@click.option(
    "--force",
    is_flag=True,
    help="Download all files even if they already exist.",
)
@click.option(
    "--sync",
    "-s",
    is_flag=True,
    help="Keep watching for new output files to download.",
)
def outputs(
    counter: str,
    download_directory: Optional[str],
    filter_download: Optional[str],
    force: bool,
    sync: bool,
) -> None:
    """
    List and download execution outputs.
    """
    if download_directory:
        download_directory = download_directory.replace("{counter}", str(counter))

    if sync:
        watch(counter, force, filter_download, download_directory)
        return

    project = get_project(require=True)
    assert project
    execution = project.get_execution_from_counter(
        counter=counter,
        params={"exclude": "outputs"},
    )
    outputs = get_execution_outputs(execution)
    if not outputs:
        warn("The execution has no outputs.")
        return
    for output in outputs:
        output["datum_url"] = f"datum://{output['id']}"
    print_table(outputs, ("name", "datum_url", "size"))
    if download_directory:
        outputs = filter_outputs(outputs, download_directory, filter_download, force)
        download_outputs(outputs, download_directory, show_success_message=True)


def watch(
    counter: str,
    force: bool,
    filter_download: Optional[str],
    download_directory: Optional[str],
) -> None:
    if download_directory:
        info(f"Downloading to: {download_directory}\nWaiting for new outputs...")
    else:
        warn("Target folder is not set. Use --download to set it.")
        return

    project = get_project(require=True)
    execution = project.get_execution_from_counter(
        counter=counter,
        params={"exclude": "outputs"},
    )
    while True:
        outputs = get_execution_outputs(execution)
        outputs = filter_outputs(outputs, download_directory, filter_download, force)
        if outputs:
            download_outputs(outputs, download_directory, show_success_message=False)
        if execution["status"] in complete_execution_statuses:
            info("Execution has finished.")
            return
        time.sleep(1)


def filter_outputs(
    outputs: List[dict],
    download_directory: str,
    filter_download: Optional[str],
    force: bool,
) -> List[dict]:
    if filter_download:
        outputs = [output for output in outputs if fnmatch(output["name"], filter_download)]
    if not force:
        # Do not download files that already exist
        outputs = [
            output
            for output in outputs
            if not os.path.isfile(os.path.join(download_directory, output["name"]))
        ]
    return outputs


def download_outputs(outputs: List[dict], output_path: str, show_success_message: bool = True) -> None:
    if not outputs:
        info("No outputs to download.")
        return
    total_size = sum(o["size"] for o in outputs)
    num_width = len(str(len(outputs)))  # How many digits required to print the number of outputs
    start_time = time.time()
    is_responding_with_content = False
    with click.progressbar(
        length=total_size,
        show_pos=True,
        item_show_func=str,
    ) as prog, requests.Session() as dl_sess:
        dl_sess.headers["User-Agent"] = f"{get_user_agent()} (downloader)"
        for i, output in enumerate(outputs, 1):
            name = output["name"]
            prog.current_item = f"({str(i).rjust(num_width)}/{str(len(outputs)).ljust(num_width)}) {name}"
            # Force visible bar for the smallest of files:
            prog.short_limit = 0  # type: ignore[attr-defined]
            download_api_resp = request(
                method="get",
                url=f"/api/v0/data/{output['id']}/download/",
                stream=is_responding_with_content,
            )
            download_api_resp.raise_for_status()
            if download_api_resp.headers.get("Content-Disposition", "").startswith("attachment"):
                # The remote server is not giving us an URL, but the actual stream!
                # We'll assume this is the case for any future downloads too, so let's turn
                # streaming automatically on for future requests.
                is_responding_with_content = True
                resp = download_api_resp
            else:
                # Otherwise, let's get the URL and download it.
                url = download_api_resp.json()["url"]
                resp = dl_sess.get(url, stream=True)
                resp.raise_for_status()
            out_path = os.path.join(output_path, name)
            out_dir = os.path.dirname(out_path)
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)

            with open(out_path, "wb") as outf:
                for chunk in resp.iter_content(chunk_size=131072):
                    prog.update(len(chunk))
                    outf.write(chunk)

    duration = time.time() - start_time
    if show_success_message:
        success(f"Downloaded {len(outputs)} outputs ({total_size} bytes) in {round(duration, 2)} seconds")
