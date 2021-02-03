import json
import os

import yaml

from valohai_cli.exceptions import CLIException


def read_data_file(path):
    ext = os.path.splitext(path)[-1].lower()
    with open(path) as infp:
        if ext == '.json':
            return json.load(infp)
        elif ext == '.yaml':
            return yaml.safe_load(infp)
        else:
            raise CLIException('Unable to load file {path}: not sure how to load {ext} files'.format(
                path=path,
                ext=ext,
            ))
