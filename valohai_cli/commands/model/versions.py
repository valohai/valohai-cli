from __future__ import annotations

from typing import Any

import click

from valohai_cli.messages import info
from valohai_cli.settings import settings
from valohai_cli.table import print_json
from valohai_cli.utils.model_utils import (
    fetch_model_versions,
    print_version_table,
    resolve_model,
)


@click.command()
@click.argument("model_name_or_id")
@click.option(
    "--count",
    "--limit",
    "-n",
    type=int,
    default=100,
    help="How many versions to show",
)
@click.option(
    "--status",
    "-s",
    multiple=True,
    type=click.Choice(["creating", "pending", "approved", "rejected"], case_sensitive=False),
    help="Filter by status",
)
@click.option("--tag", "-t", multiple=True, help="Filter by tag")
def versions(model_name_or_id: str, count: int, status: tuple[str, ...], tag: tuple[str, ...]) -> None:
    """
    List versions of a model.

    MODEL_NAME_OR_ID can be a model name (prefix match) or UUID.
    """
    model = resolve_model(model_name_or_id)

    params: dict[str, Any] = {"limit": count}
    if status:
        params["status"] = list(status)
    if tag:
        params["tags"] = ",".join(tag)

    data = fetch_model_versions(model["id"], params)

    if settings.output_format == "json":
        return print_json(data)

    if not data:
        info(f"{model['name']}: No matching versions.")
        return

    print_version_table(data)
