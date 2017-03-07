from valohai_cli.cli import cli


def test_command_enumeration():
    assert 'init' in cli.list_commands(None)
    assert cli.get_command(None, 'init')
