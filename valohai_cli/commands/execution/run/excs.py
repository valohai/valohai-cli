import click

from valohai_cli.exceptions import APIError
from valohai_cli.utils.api_error_utils import find_error


class ExecutionCreationAPIError(APIError):
    def get_hints(self):
        try:
            error_json = self.response.json()
            assert isinstance(error_json, dict)
        except:
            return

        if find_error(error_json.get('environment'), code='does_not_exist'):
            yield 'Run `{}` to see the complete list of available environments.'.format(
                click.style('vh environments', bold=True),
            )
