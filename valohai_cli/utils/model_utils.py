from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import click

from valohai_cli.api import request
from valohai_cli.table import print_table
from valohai_cli.utils.matching import match_from_list_with_error

VERSION_TABLE_COLUMNS = ["counter", "status", "source_str", "tags_str", "dataset_version_name", "ctime"]
VERSION_TABLE_HEADERS = ["#", "Status", "Source", "Tags", "Dataset Version", "Created"]


def resolve_model(name_or_id: str) -> dict:
    """
    Resolve a model by name (prefix match) or UUID.

    Returns the full model detail dict from the API.
    """
    if _looks_like_uuid(name_or_id):
        resp = request("get", f"/api/v0/models/{name_or_id}/", handle_errors=False)
        if resp.status_code == 200:
            return resp.json()

    results = request(
        "get",
        "/api/v0/models/",
        params={"limit": 200, "ordering": "name"},
    ).json()["results"]

    if not results:
        raise click.ClickException("No models found.")

    names = [m["name"] for m in results]
    matched_name = match_from_list_with_error(names, name_or_id, noun="model")
    model = next(m for m in results if m["name"] == matched_name)
    return request("get", f"/api/v0/models/{model['id']}/").json()


def resolve_model_version(model_id: str, counter_or_id: str) -> dict:
    """
    Resolve a model version by counter number or UUID.
    """
    if _looks_like_uuid(counter_or_id):
        resp = request("get", f"/api/v0/model-versions/{counter_or_id}/", handle_errors=False)
        if resp.status_code == 200:
            return resp.json()

    try:
        counter = int(counter_or_id)
    except ValueError:
        raise click.ClickException(
            f"{counter_or_id!r} is not a valid version counter or UUID.",
        )

    results = request(
        "get",
        "/api/v0/model-versions/",
        params={"model": model_id, "counter": counter, "limit": 1},
    ).json()["results"]

    if not results:
        raise click.ClickException(f"No version #{counter} found for this model.")

    return results[0]


def fetch_model_versions(model_id: str, params: dict[str, Any] | None = None) -> list[dict]:
    """Fetch model versions from the API."""
    base_params: dict[str, Any] = {"model": model_id, "limit": 100}
    if params:
        base_params.update(params)
    return request("get", "/api/v0/model-versions/", params=base_params).json()["results"]


def enrich_version(version: dict) -> None:
    """Add display-friendly fields to a version dict, in place."""
    version["source_str"] = format_version_source(version)
    tags = version.get("tags", [])
    version["tags_str"] = ", ".join(tags) if tags else ""
    dv = version.get("dataset_version")
    version["dataset_version_name"] = dv.get("name", "") if dv else ""


def print_version_table(versions: list[dict]) -> None:
    """Enrich and print a table of model versions."""
    for v in versions:
        enrich_version(v)
    print_table(
        versions,
        columns=VERSION_TABLE_COLUMNS,
        headers=VERSION_TABLE_HEADERS,
    )


def format_version_source(version: dict) -> str:
    """Extract a human-readable source string from a version dict."""
    source = version.get("source", {})
    return source.get("title") or source.get("type", "")


def generate_markdown_descriptions(descriptions: Any) -> Iterator[str]:
    """Yield markdown-formatted description lines."""
    if not descriptions or not isinstance(descriptions, list):
        return
    non_empty = [d for d in descriptions if d.get("body")]
    if not non_empty:
        return
    yield "## Descriptions"
    yield ""
    for desc in non_empty:
        heading = desc.get("title") or desc.get("category", "")
        if heading:
            yield f"### {heading}"
            yield ""
        yield desc["body"]
        yield ""


def _looks_like_uuid(s: str) -> bool:
    """Check if a string looks like a UUID (with or without dashes)."""
    clean = s.replace("-", "")
    return len(clean) == 32 and all(c in "0123456789abcdef" for c in clean.lower())
