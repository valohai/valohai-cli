from __future__ import annotations

import fnmatch
from typing import Any

import click

from valohai_cli.models.project import Project


def parse_reuse_spec(spec: str) -> tuple[str, list[str]]:
    """
    Parse a --reuse spec of the form "pipeline-counter:glob1,glob2,...".

    Returns (pipeline_counter, [glob1, glob2, ...]).
    """
    if ":" not in spec:
        raise click.UsageError(
            f"Invalid --reuse format: {spec!r}. Expected format: pipeline-counter:node-glob,node-glob,...",
        )
    counter_part, _, globs_part = spec.partition(":")
    counter_part = counter_part.strip()
    if not counter_part:
        raise click.UsageError("--reuse: pipeline counter must not be empty")
    globs = [g.strip() for g in globs_part.split(",") if g.strip()]
    if not globs:
        raise click.UsageError(f"--reuse: no node globs specified in {spec!r}")
    return (counter_part, globs)


def fetch_source_pipeline_nodes(project: Project, counter: str) -> dict[str, str]:
    """
    Fetch a pipeline by counter and return a mapping of node name -> node ID.
    """
    pipeline_data = project.get_pipeline_from_counter(counter)
    nodes: dict[str, str] = {}
    for node in pipeline_data.get("nodes", []):
        name = node.get("name")
        node_id = node.get("id")
        if name and node_id:
            nodes[name] = node_id
    return nodes


def apply_reuse_to_pipeline(
    *,
    converted_nodes: list[dict[str, Any]],
    reuse_specs: list[str],
    project: Project,
) -> None:
    """
    For each --reuse spec, fetch the source pipeline and replace matching
    nodes with mimic nodes referencing the source pipeline's nodes.
    """
    reuses = {}
    for spec in reuse_specs:
        counter, globs = parse_reuse_spec(spec)
        source_nodes = fetch_source_pipeline_nodes(project, counter)
        matched_any = False

        for i, node in enumerate(converted_nodes):
            node_name = node["name"]
            if any(fnmatch.fnmatch(node_name, g) for g in globs):
                if node_name not in source_nodes:
                    raise click.UsageError(
                        f"Node {node_name!r} matched by --reuse glob but not found "
                        f"in source pipeline ={counter} "
                        f"(available nodes: {sorted(source_nodes)})",
                    )
                converted_nodes[i] = {
                    "type": "mimic",
                    "name": node_name,
                    "source": source_nodes[node_name],
                }
                reuses[node_name] = counter
                matched_any = True

        if not matched_any:
            available = [n["name"] for n in converted_nodes]
            raise click.UsageError(
                f"--reuse={spec!r}: no nodes matched the given globs. Available nodes: {sorted(available)}",
            )

    if reuses:
        reuse_descs = ", ".join(f"={counter}: {node_name}" for node_name, counter in sorted(reuses.items()))
        click.echo(f"Reusing nodes: {reuse_descs}")
