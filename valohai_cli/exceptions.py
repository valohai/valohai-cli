import click
from click import ClickException


class APIError(ClickException):
    def __init__(self, response):
        super(APIError, self).__init__(response.text)
        self.response = response
        self.request = response.request

    def show(self, file=None):
        click.secho('Error: %s' % self.format_message(), file=file, err=True, fg='red')


class ConfigurationError(RuntimeError):
    pass
