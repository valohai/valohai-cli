from __future__ import annotations

import click
import pytest

from valohai_cli.commands.pipeline.run.reuse import apply_reuse_to_pipeline, parse_reuse_spec

ALL_SOURCE_NODES = [
    {"name": "pretrain", "id": "uuid-pretrain"},
    {"name": "mangle", "id": "uuid-mangle"},
    {"name": "train", "id": "uuid-train"},
]


def _make_nodes():
    return [
        {"type": "execution", "name": "pretrain", "template": {}},
        {"type": "execution", "name": "mangle", "template": {}},
        {"type": "execution", "name": "train", "template": {}},
    ]


def _make_project(source_nodes):
    class MockProject:
        def get_pipeline_from_counter(self, counter, params=None):
            return {"nodes": source_nodes}

    return MockProject()


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("latest:pretrain,mangle", ("latest", ["pretrain", "mangle"])),
        ("42:train*", ("42", ["train*"])),
        ("latest: pretrain , mangle ", ("latest", ["pretrain", "mangle"])),
    ],
)
def test_parse_reuse_spec(spec, expected):
    assert parse_reuse_spec(spec) == expected


@pytest.mark.parametrize(
    ("spec", "match"),
    [
        ("latest", "Invalid --reuse format"),
        (":pretrain", "pipeline counter must not be empty"),
        ("latest:", "no node globs specified"),
    ],
)
def test_parse_reuse_spec_errors(spec, match):
    with pytest.raises(click.UsageError, match=match):
        parse_reuse_spec(spec)


def test_apply_reuse_glob_matching():
    nodes = _make_nodes()
    project = _make_project(ALL_SOURCE_NODES)

    apply_reuse_to_pipeline(
        converted_nodes=nodes,
        reuse_specs=["5:*train"],
        project=project,
    )

    assert nodes[0] == {"type": "mimic", "name": "pretrain", "source": "uuid-pretrain"}
    assert nodes[1]["type"] == "execution"
    assert nodes[2] == {"type": "mimic", "name": "train", "source": "uuid-train"}


def test_apply_reuse_node_not_in_source_raises():
    nodes = _make_nodes()
    project = _make_project([{"name": "train", "id": "uuid-train"}])

    with pytest.raises(click.UsageError, match="not found in source pipeline"):
        apply_reuse_to_pipeline(
            converted_nodes=nodes,
            reuse_specs=["latest:pretrain"],
            project=project,
        )
