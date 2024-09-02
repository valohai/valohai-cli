import math

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table


def convert_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


@click.command()
@click.option(
    "--count",
    "--limit",
    "-n",
    type=int,
    default=100,
    help="How many datums to show",
)
def list(count: int) -> None:
    """
    Show a list of data in the project.
    """
    params = {
        "limit": count,
        "ordering": "-ctime",
        "deleted": "false",
        "no_count": "true",
    }
    project = get_project(require=True)
    assert project
    if project:
        params["project"] = project.id

    data = request("get", "/api/v0/data/", params=params).json()["results"]
    if settings.output_format == "json":
        return print_json(data)
    if not data:
        info(f"{project}: No data.")
        return
    for datum in data:
        datum["url"] = f'datum://{datum["id"]}'
        datum["execution_string"] = (
            "Not from exec" if not datum["output_execution"] else f'#{datum["output_execution"]["counter"]}'
        )
        datum["size"] = convert_size(datum["size"])
        datum["uri"] = "No URI" if not datum["uri"] else datum["uri"]

    print_table(
        data,
        columns=["name", "size", "execution_string", "ctime", "url", "uri"],
        headers=["Name", "Size", "Output of Exec", "Created At", "URL", "URI"],
    )
