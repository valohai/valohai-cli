from __future__ import annotations

import click

from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table
from valohai_cli.utils import humanize_identifier
from valohai_cli.utils.model_utils import (
    fetch_model_versions,
    print_version_table,
    resolve_model,
)


@click.command()
@click.argument("model_name_or_id")
def info(model_name_or_id: str) -> None:
    """
    Show details about a model.

    MODEL_NAME_OR_ID can be a model name (prefix match) or UUID.
    """
    detail = resolve_model(model_name_or_id)

    if settings.output_format == "json":
        return print_json(detail)

    ignored_keys = {
        "id",
        "url",
        "version_summary",
        "associated_project_ids",
        "associated_projects",
        "teams",
        "descriptions",
    }

    data = {
        humanize_identifier(key): str(value)
        for key, value in detail.items()
        if key not in ignored_keys and not isinstance(value, (dict, list))
    }
    data["owner"] = detail.get("owner", {}).get("username", "")
    data["creator"] = detail.get("creator", {}).get("username", "")

    tags = detail.get("tags", [])
    if tags:
        data["tags"] = ", ".join(tags)

    projects = detail.get("associated_projects", [])
    if projects:
        data["projects"] = ", ".join(p.get("name") or p.get("id", str(p)) for p in projects)

    print_table(data)

    versions = fetch_model_versions(detail["id"])
    if versions:
        click.echo()
        print_version_table(versions)
