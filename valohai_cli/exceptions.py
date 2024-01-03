from pprint import pformat
from typing import Any, Iterable, Optional, Union

import click
from click import ClickException
from requests.models import Response


class CLIException(ClickException):
    kind: str = 'Error'
    color: str = 'red'

    def __init__(self, message: str, kind: Optional[str] = None) -> None:
        super().__init__(message)
        self.kind = str(kind or self.kind)

    def show(self, file: Optional[Any] = None) -> None:
        formatted_message = self.format_message()
        if formatted_message and '\n' in formatted_message:
            # If there are newlines in the message, we'll format things a little differently.
            # Namely, the entire message is on a separate line, and to avoid "color fatigue",
            # it's not all red.
            click.secho(f'{self.kind}:', file=file, err=True, fg=self.color)
            click.secho(formatted_message, file=file, err=True)
        else:
            text = f'{self.kind}: {formatted_message}'
            click.secho(text, file=file, err=True, fg=self.color)

        hints = list(self.get_hints())
        if hints:
            click.secho('\nHint:', bold=True, err=True)
            for hint in hints:
                click.echo(f'* {hint}', err=True)

    def get_hints(self) -> Iterable[str]:
        return []


class APIError(CLIException):
    kind = 'API Error'

    def __init__(self, response: Response) -> None:
        # Don't shower the user with a blob of HTML
        text = ('Internal error' if '<!DOCTYPE html>' in response.text else response.text)
        super().__init__(text)
        self.response = response
        self.request = response.request

    @property
    def error_json(self) -> Union[None, dict, list]:
        try:
            error_json = self.response.json()
            if isinstance(error_json, (dict, list)):
                return error_json
        except Exception:
            pass
        return None

    @property
    def code(self) -> Optional[Any]:
        """
        Attempt to retrieve a top-level error code from the response.
        """
        error_json = self.error_json
        if isinstance(error_json, dict):
            return error_json.get('code')
        return None

    def format_message(self) -> str:
        try:
            error_json = self.error_json
            if error_json:
                from .utils.error_fmt import format_error_data
                try:
                    return format_error_data(error_json)
                except Exception:
                    return pformat(error_json, indent=2)  # This should be more readable than raw JSON
        except Exception:
            pass
        return super().format_message()


class APINotFoundError(APIError):
    kind = 'Not Found'


class ConfigurationError(CLIException, RuntimeError):
    kind = 'Configuration Error'


class NotLoggedIn(ConfigurationError):
    pass


class NoProject(CLIException):
    color = 'yellow'


class NoExecution(CLIException):
    color = 'yellow'


class InvalidConfig(CLIException):
    pass


class PackageTooLarge(CLIException):
    pass


class APIConnectionError(CLIException):
    pass


class NoGitRepo(CLIException):
    color = 'yellow'

    def __init__(self, directory: str) -> None:
        self.directory = directory
        super().__init__(f'{directory} is not a Git repository')


class NoCommit(ValueError, CLIException):
    color = 'yellow'

    def __init__(self, directory: str) -> None:
        self.directory = directory
        super().__init__(f'{directory} has no commits')
