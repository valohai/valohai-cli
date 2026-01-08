import os

import pytest

from tests.fixtures.config import BROKEN_CONFIG_YAML, CONFIG_YAML, INVALID_CONFIG_YAML
from valohai_cli.commands.lint import lint
from valohai_cli.utils import get_project_directory

cases = {
    "valid": {
        "data": CONFIG_YAML,
        "output": "No errors",
        "exit_code": 0,
    },
    "invalid": {
        "data": INVALID_CONFIG_YAML,
        "output": "There were 5 total errors",
        "exit_code": 5,
    },
    "broken": {
        "data": BROKEN_CONFIG_YAML,
        "output": "line 1, column 2",
        "exit_code": 1,
    },
}


@pytest.mark.parametrize("case", ("valid", "invalid", "broken"))
@pytest.mark.parametrize("pass_explicit", (False, True))
def test_lint(runner, case, pass_explicit):
    case = cases[case]
    filename = os.path.join(get_project_directory(), "valohai.yaml")
    with open(filename, "w") as yaml_fp:
        yaml_fp.write(case["data"])
    args = [filename] if pass_explicit else []
    rv = runner.invoke(lint, args, catch_exceptions=False)
    assert rv.exit_code == case["exit_code"]
    assert case["output"] in rv.output
