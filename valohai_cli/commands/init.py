import click


@click.command()
def init():
    click.secho('hello', fg='green')
