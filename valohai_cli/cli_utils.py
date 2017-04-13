import click


def prompt_from_list(options, prompt, nonlist_validator=None):
    for i, option in enumerate(options, 1):
        click.echo('{number} {name} {description}'.format(
            number=click.style('[%3d]' % i, fg='cyan'),
            name=option['name'],
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
        click.secho('Sorry, try again.')
        continue
