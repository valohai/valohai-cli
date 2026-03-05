from __future__ import annotations

from typing import Any

import click

from valohai_cli.api import request
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
    help="How many models to show",
)
@click.option("--tag", "-t", multiple=True, help="Filter by tag")
@click.option("--name", help="Filter by name (substring match)")
@click.option("--quiet", "-q", is_flag=True, help="Print only names and IDs, one per line")
def list(count: int, tag: tuple[str, ...], name: str | None, quiet: bool) -> None:
    """
    List models in the catalog.
    """
    params: dict[str, Any] = {
        "limit": count,
    }
    if tag:
        params["tags"] = ",".join(tag)
    if name:
        params["name"] = name

    data = request("get", "/api/v0/models/", params=params).json()["results"]

    if settings.output_format == "json":
        return print_json(data)

    if not data:
        info("No models found.")
        return

    if quiet:
        for item in data:
            click.echo(f"{item['name']}\t{item['id']}")
        return

    for item in data:
        item["owner_name"] = item.get("owner", {}).get("username", "")
        tag_list = item.get("tags", [])
        item["tags_str"] = ", ".join(tag_list) if tag_list else ""
        versions = item.get("version_summary", [])
        item["n_versions"] = str(len(versions))

    print_table(
        data,
        columns=["name", "owner_name", "n_versions", "tags_str", "ctime"],
        headers=["Name", "Owner", "Versions", "Tags", "Created"],
    )
