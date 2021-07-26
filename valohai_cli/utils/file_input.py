import json
import os
from typing import Any

import yaml

from valohai_cli.exceptions import CLIException


def read_data_file(path: str) -> Any:
    ext = os.path.splitext(path)[-1].lower()
    with open(path) as infp:
        if ext == '.json':
            return json.load(infp)
        elif ext == '.yaml':
            return yaml.safe_load(infp)
    raise CLIException(f'Unable to load file {path}: not sure how to load {ext} files')
