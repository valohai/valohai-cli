import click

from valohai_cli.exceptions import CLIException
from valohai_cli.utils.cli_utils import counter_argument
from valohai_cli.utils.ssh import (
    get_ssh_details_with_retry,
    make_ssh_connection,
    select_private_key_from_possible_directories,
)


@click.command()
@counter_argument
@click.option(
    "--private-key-file",
    default=None,
    type=click.Path(file_okay=True, exists=True),
    help="Private SSH key to use for the connection.",
)
@click.option(
    "--address",
    default=None,
    help='Address of the container in "ip:port" format. If not provided, '
    "the address from the execution will be used.",
)
def ssh(counter: int, private_key_file: str, address: str) -> None:
    """
    Make SSH Connection to the execution container.
    """
    if address:
        try:
            ip_address, _, port_str = address.partition(":")
            if not ip_address or not port_str:
                raise CLIException("Address must be in 'ip:port' format.")
            port = int(port_str)
            if port <= 1023:
                raise CLIException("Port must be above 1023")
        except ValueError as e:
            raise CLIException(f"Invalid address format: {e}")
    else:
        ip_address, port = get_ssh_details_with_retry(counter)

    click.echo(f"SSH address is {ip_address}:{port}")
    if not private_key_file:
        private_key_file = select_private_key_from_possible_directories()
    make_ssh_connection(ip_address, port, private_key_file)
