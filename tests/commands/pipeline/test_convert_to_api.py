import json

import pytest

from tests.fixtures.config import PIPELINE_YAML
from tests.utils import write_yaml_config
from valohai_cli.commands.pipeline.convert_to_api import convert_to_api


@pytest.mark.parametrize("indent", [None, 0, 1])
def test_convert_to_api(runner, logged_in_and_linked, indent):
    write_yaml_config(PIPELINE_YAML)
    args = ["--commit=main", "Train Pipeline"]
    if indent is not None:
        args += [f"--indent={indent}"]
    result = runner.invoke(convert_to_api, args)

    assert result.exit_code == 0
    output = json.loads(result.output)

    assert "pipeline_max_steps" in output["parameters"]
    assert "sources" in output["parameters"]
    assert len(output["edges"]) == 5  # 5 edges defined in the pipeline
    assert len(output["nodes"]) == 3  # preprocess, train, evaluate
