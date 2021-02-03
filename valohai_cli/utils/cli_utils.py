import click

from valohai_cli.help_texts import EXECUTION_COUNTER_HELP


def _default_name_formatter(option):
    return option['name']


def prompt_from_list(options, prompt, nonlist_validator=None, name_formatter=_default_name_formatter):
    for i, option in enumerate(options, 1):
        click.echo('{number} {name} {description}'.format(
            number=click.style('[%3d]' % i, fg='cyan'),
            name=name_formatter(option),
            description=(
                click.style('(%s)' % option['description'], dim=True)
                if option.get('description')
                else ''
            ),
        ))
    while True:
        answer = click.prompt(prompt)
        if answer.isdigit() and (1 <= int(answer) <= len(options)):
            return options[int(answer) - 1]
        if nonlist_validator:
            retval = nonlist_validator(answer)
            if retval:
                return retval
        for option in options:
            if answer == option['name']:
                return option
        click.secho('Sorry, try again.')
        continue


class HelpfulArgument(click.Argument):
    def __init__(self, param_decls, **kwargs):
        self.help = kwargs.pop('help', None)
        super().__init__(param_decls, **kwargs)

    def get_help_record(self, ctx):
        if self.help:
            return (self.name, self.help)


def counter_argument(fn):
    # Extra gymnastics needed because `click.arguments` mutates the kwargs here
    return click.argument('counter', help=EXECUTION_COUNTER_HELP, cls=HelpfulArgument)(fn)
