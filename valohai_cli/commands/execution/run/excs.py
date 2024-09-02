from typing import Iterable

import click

from valohai_cli.exceptions import APIError
from valohai_cli.utils.api_error_utils import find_error


class ExecutionCreationAPIError(APIError):
    def get_hints(self) -> Iterable[str]:
        try:
            error_json = self.response.json()
        except Exception:
            return

        if not isinstance(error_json, dict):
            return

        if find_error(error_json.get("environment"), code="does_not_exist"):
            yield (
                f'Run `{click.style("vh environments", bold=True)}` to see '
                f'the complete list of available environments.'
            )
