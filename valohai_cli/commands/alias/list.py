import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table


@click.command()
@click.option(
    "--count",
    "--limit",
    "-n",
    type=int,
    default=100,
    help="How many aliases to show",
)
def list(count: int) -> None:
    """
    Show a list of data aliases in the project.
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

    aliases = request("get", "/api/v0/datum-aliases/", params=params).json()["results"]
    if settings.output_format == "json":
        return print_json(aliases)
    if not aliases:
        info(f"{project}: No data aliases.")
        return
    for alias in aliases:
        alias["url"] = f'datum://{alias["name"]}'
        alias["datum"] = "No target" if not alias["datum"] else alias["datum"]["name"]

    print_table(
        aliases,
        columns=["name", "datum", "mtime", "url"],
        headers=["Name", "Data", "Last Modified", "URL"],
    )
