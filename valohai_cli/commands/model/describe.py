from __future__ import annotations

from collections.abc import Iterator

import click

from valohai_cli.utils.model_utils import (
    enrich_version,
    fetch_model_versions,
    generate_markdown_descriptions,
    resolve_model,
)


@click.command()
@click.argument("model_name_or_id")
@click.option(
    "--versions/--no-versions",
    default=True,
    help="Include version listing (default: yes)",
)
def describe(model_name_or_id: str, versions: bool) -> None:
    """
    Describe a model in Markdown format (for LLM agent use).

    Outputs a structured Markdown document to stdout with the model's
    metadata, tags, associated projects, descriptions, and version history.

    MODEL_NAME_OR_ID can be a model name (prefix match) or UUID.
    """
    detail = resolve_model(model_name_or_id)
    click.echo("\n".join(_generate_markdown(detail)))
    if versions:
        click.echo("\n".join(_generate_versions_section(detail)))


def _generate_markdown(detail: dict) -> Iterator[str]:
    yield f"# Model: {detail['name']}"
    yield ""
    yield from _generate_metadata_section(detail)
    yield from _generate_tags_section(detail)
    yield from generate_markdown_descriptions(detail.get("descriptions"))
    yield from _generate_projects_section(detail)


def _generate_versions_section(detail: dict) -> Iterator[str]:
    version_list = fetch_model_versions(detail["id"])
    if version_list:
        yield "## Versions"
        yield ""
        yield "| # | Status | Source | Tags | Dataset Version | Created |"
        yield "|---|--------|--------|------|-----------------|---------|"
        for v in version_list:
            enrich_version(v)
            yield (
                f"| {v.get('counter', '?')} | {v.get('status', '')} "
                f"| {v['source_str']} | {v['tags_str']} "
                f"| {v['dataset_version_name']} | {v.get('ctime', '')} |"
            )
        yield ""


def _generate_projects_section(detail: dict) -> Iterator[str]:
    if projects := detail.get("associated_projects", []):
        yield "## Associated Projects"
        yield ""
        for proj in projects:
            name = proj.get("name") or proj.get("id", str(proj))
            yield f"- {name}"
        yield ""


def _generate_tags_section(detail: dict) -> Iterator[str]:
    if tags := detail.get("tags", []):
        yield "## Tags"
        yield ""
        yield ", ".join(f"`{t}`" for t in tags)
        yield ""


def _generate_metadata_section(detail: dict) -> Iterator[str]:
    yield "## Metadata"
    yield ""
    yield f"- **ID:** `{detail['id']}`"
    yield f"- **Slug:** `{detail.get('slug', '')}`"
    yield f"- **Owner:** {detail.get('owner', {}).get('username', 'N/A')}"
    yield f"- **Creator:** {detail.get('creator', {}).get('username', 'N/A')}"
    yield f"- **Access mode:** {detail.get('access_mode', 'N/A')}"
    yield f"- **Created:** {detail.get('ctime', 'N/A')}"
    yield f"- **Modified:** {detail.get('mtime', 'N/A')}"
    if detail.get("archived", False):
        yield "- **Archived:** yes"
    yield ""
