import click
from click import ClickException


class CLIException(ClickException):
    kind = 'Error'
    color = 'red'

    def __init__(self, *args, **kwargs):
        kind = kwargs.pop('kind', None)
        super(CLIException, self).__init__(*args, **kwargs)
        self.kind = (kind or self.kind)

    def show(self, file=None):
        text = '{kind}: {message}'.format(kind=self.kind, message=self.format_message())
        click.secho(text, file=file, err=True, fg=self.color)


class APIError(CLIException):

    def __init__(self, response):
        super(APIError, self).__init__(response.text)
        self.response = response
        self.request = response.request


class ConfigurationError(CLIException, RuntimeError):
    pass


class NotLoggedIn(ConfigurationError):
    pass


class NoProject(CLIException):
    color = 'yellow'


class NoExecution(CLIException):
    color = 'yellow'


class InvalidConfig(CLIException):
    pass


class NoGitRepo(CLIException):
    color = 'yellow'

    def __init__(self, directory):
        self.directory = directory
        super(NoGitRepo, self).__init__('{} is not a Git repository'.format(directory))
