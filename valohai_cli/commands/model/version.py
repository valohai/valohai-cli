from __future__ import annotations

from collections.abc import Iterator

import click

from valohai_cli.api import request
from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table
from valohai_cli.utils import humanize_identifier
from valohai_cli.utils.model_utils import (
    format_version_source,
    generate_markdown_descriptions,
    resolve_model,
    resolve_model_version,
)


@click.command()
@click.argument("model_name_or_id")
@click.argument("version_counter_or_id")
@click.option(
    "--describe",
    "describe_mode",
    is_flag=True,
    help="Output as Markdown (for LLM agent use)",
)
def version(model_name_or_id: str, version_counter_or_id: str, describe_mode: bool) -> None:
    """
    Show details about a specific model version.

    MODEL_NAME_OR_ID can be a model name (prefix match) or UUID.
    VERSION_COUNTER_OR_ID can be a version counter number or UUID.
    """
    model = resolve_model(model_name_or_id)
    ver = resolve_model_version(model["id"], version_counter_or_id)
    ver_id = ver["id"]

    source_exec_list = _fetch_optional_list(f"/api/v0/model-versions/{ver_id}/source-executions/")
    source_data_list = _fetch_optional_list(f"/api/v0/model-versions/{ver_id}/source-data/")

    if describe_mode:
        click.echo("\n".join(_generate_markdown(ver, model, source_exec_list, source_data_list)))
        return

    if settings.output_format == "json":
        return print_json({
            "version": ver,
            "source_executions": source_exec_list,
            "source_data": source_data_list,
        })

    _print_table(ver, source_exec_list, source_data_list)


def _fetch_optional_list(url: str) -> list[dict]:
    """Fetch a list endpoint that may return 404, returning [] on 404."""
    resp = request("get", url, handle_errors=False)
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    return resp.json().get("results", [])


def _print_table(ver: dict, source_exec_list: list, source_data_list: list) -> None:
    ignored_keys = {"id", "model", "dataset_aliases", "descriptions", "notes", "dataset_version"}

    data = {
        humanize_identifier(key): str(value)
        for key, value in ver.items()
        if key not in ignored_keys and not isinstance(value, (dict, list))
    }
    data["source"] = format_version_source(ver)
    data["creator"] = ver.get("creator", {}).get("username", "")

    dv = ver.get("dataset_version")
    if dv:
        data["dataset version"] = dv.get("name", "")

    tags = ver.get("tags", [])
    if tags:
        data["tags"] = ", ".join(tags)

    print_table(data)

    if source_exec_list:
        click.echo()
        click.secho("Source Executions:", bold=True)
        print_table(
            source_exec_list,
            columns=["counter", "status", "step", "ctime"],
            headers=["#", "Status", "Step", "Created"],
        )

    if source_data_list:
        click.echo()
        click.secho("Source Data:", bold=True)
        for d in source_data_list:
            d["size_str"] = str(d.get("size", ""))
        print_table(
            source_data_list,
            columns=["name", "size_str", "ctime"],
            headers=["Name", "Size", "Created"],
        )


def _generate_markdown(
    ver: dict,
    model: dict,
    source_exec_list: list,
    source_data_list: list,
) -> Iterator[str]:
    yield f"# Model Version: {model['name']} #{ver.get('counter', '?')}"
    yield ""

    yield from _generate_metadata_section(model, ver)
    yield from _generate_tags_section(ver)
    yield from generate_markdown_descriptions(ver.get("descriptions"))
    yield from _generate_notes_section(ver)
    yield from _generate_source_execs_section(source_exec_list)
    yield from _generate_source_data_section(source_data_list)


def _generate_source_data_section(source_data_list: list) -> Iterator[str]:
    if source_data_list:
        yield "## Source Data"
        yield ""
        yield "| Name | Size | Created |"
        yield "|------|------|---------|"
        for d in source_data_list:
            yield f"| {d.get('name', '')} | {d.get('size', '')} | {d.get('ctime', '')} |"
        yield ""


def _generate_source_execs_section(source_exec_list: list) -> Iterator[str]:
    if source_exec_list:
        yield "## Source Executions"
        yield ""
        yield "| # | Status | Step | Created |"
        yield "|---|--------|------|---------|"
        for ex in source_exec_list:
            yield (
                f"| {ex.get('counter', '?')} | {ex.get('status', '')} | {ex.get('step', '')} | {ex.get('ctime', '')} |"
            )
        yield ""


def _generate_notes_section(ver: dict) -> Iterator[str]:
    notes = ver.get("notes")
    if not isinstance(notes, list):
        return
    non_empty_notes = [n for n in notes if isinstance(n, dict) and n.get("body")]
    if not non_empty_notes:
        return
    yield "## Notes"
    yield ""
    for note in non_empty_notes:
        heading = note.get("title", "")
        if heading:
            yield f"### {heading}"
            yield ""
        yield note["body"]
        yield ""


def _generate_tags_section(ver: dict) -> Iterator[str]:
    if tags := ver.get("tags", []):
        yield "## Tags"
        yield ""
        yield ", ".join(f"`{t}`" for t in tags)
        yield ""


def _generate_metadata_section(model: dict, ver: dict) -> Iterator[str]:
    yield "## Metadata"
    yield ""
    yield f"- **Version ID:** `{ver['id']}`"
    yield f"- **Model:** {model['name']} (`{model['id']}`)"
    yield f"- **Counter:** {ver.get('counter', '?')}"
    yield f"- **Status:** {ver.get('status', 'N/A')}"
    source_str = format_version_source(ver)
    source = ver.get("source", {})
    if source_str:
        yield f"- **Source:** {source_str} ({source.get('type', '')})"
    yield f"- **Creator:** {ver.get('creator', {}).get('username', 'N/A')}"
    yield f"- **Created:** {ver.get('ctime', 'N/A')}"
    yield f"- **Modified:** {ver.get('mtime', 'N/A')}"
    yield f"- **Execution count:** {ver.get('execution_count', 0)}"
    dv = ver.get("dataset_version")
    if dv:
        yield f"- **Dataset version:** {dv.get('name', '')} (`{dv.get('id', '')}`)"
    yield ""
