import pytest

from valohai_cli.commands.project.create import create
from valohai_cli.utils import get_random_string

from .utils import get_project_mock


@pytest.mark.parametrize("link", (False, True))
def test_create(runner, logged_in, link):
    name = get_random_string()
    with get_project_mock(name):
        result = runner.invoke(create, ["-n", name, ("--link" if link else "--no-link")])
        assert (f"{name} created") in result.output
        if link:
            assert "Linked" in result.output


@pytest.mark.parametrize("input", ("y", "n"))
def test_create_linked(runner, logged_in_and_linked, input):
    name = get_random_string()
    with get_project_mock(name):
        result = runner.invoke(create, ["-n", name], input=input)
        if input == "y":
            assert (f"{name} created") in result.output
            assert "Linked" in result.output
