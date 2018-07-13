import click

from valohai_cli.ctx import get_project
from valohai_cli.utils import open_browser
from valohai_cli.utils.cli_utils import counter_argument


@click.command()
@counter_argument
def open(counter):
    """
    Open an execution in a web browser.
    """
    execution = get_project(require=True).get_execution_from_counter(counter=counter)
    open_browser(execution)
