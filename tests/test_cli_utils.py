import click
import pytest

from valohai_cli.utils.cli_utils import PriorityHackCommand, priority_option


@click.command(
    cls=PriorityHackCommand,
    context_settings={"ignore_unknown_options": True},
)
@click.option("--foo/--no-foo")
@priority_option
def command(priority: int | None, foo: str | None):
    click.echo(f"{priority=}, {foo=}")


@pytest.mark.parametrize(
    "case,expected",
    [
        (["--priority=5"], {"priority": 5}),
        (["--priority", "-1"], {"priority": -1}),  # Split -1 parsed right
        (["--priority", "--foo"], {"priority": 1}),  # Implicit +1
    ],
)
def test_priority_hack_command_parsing(case, expected):
    ctx = click.Context(command)
    command.parse_args(ctx, case)
    for key, value in expected.items():
        assert ctx.params[key] == value
