import sys

import click
import requests

import valohai_cli
from valohai_cli.messages import warn


@click.command()
def update_check():
    data = get_pypi_info()
    current_version = valohai_cli.__version__
    latest_version = data['info']['version']
    click.echo('Your version of Valohai-CLI is ' + click.style(current_version, bold=True))
    click.echo(' The latest release on PyPI is ' + click.style(latest_version, bold=True))
    upgrade_status = determine_upgrade_status(current_version, latest_version)

    if upgrade_status == 'upgrade':
        click.secho(
            '\nGood news! An upgrade is available!\n'
            'Run (e.g.) `pip install -U valohai-cli` to install the new version.',
            bold=True,
            fg='green',
        )
        click.echo('Upgrade instructions may differ based on the method you\'ve installed the application with.')
        sys.exit(1)
    elif upgrade_status == 'delorean':
        click.secho(
            '\nWhen this thing gets up to 88 mph... You seem to be running a version from the future!\n',
            bold=True,
            fg='cyan',
        )
    elif upgrade_status == 'current':
        click.echo('\nYou seem to be running the latest and greatest. Good on you!')


def determine_upgrade_status(current_version, latest_version):
    try:
        from distutils.version import LooseVersion
        current_version = LooseVersion(current_version)
        latest_version = LooseVersion(latest_version)
        if latest_version > current_version:
            return 'upgrade'
        elif latest_version < current_version:
            return 'delorean'
        elif latest_version == current_version:
            return 'current'
    except Exception as exc:
        warn('Unable to determine whether the version is older or newer (%s)' % exc)
    return None


def get_pypi_info():
    resp = requests.get('https://pypi.org/pypi/valohai-cli/json')
    resp.raise_for_status()
    return resp.json()
