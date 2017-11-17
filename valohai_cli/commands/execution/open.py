import click

from valohai_cli.ctx import get_project
from valohai_cli.utils import open_browser


@click.command()
@click.argument('counter')
def open(counter):
    """
    Open an execution in a web browser.
    """
    execution = get_project(require=True).get_execution_from_counter(counter=counter)
    open_browser(execution)
