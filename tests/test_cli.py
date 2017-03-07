from valohai_cli.cli import PluginCLI


def test_command_enumeration():
    cli = PluginCLI()
    assert 'init' in cli.list_commands(None)
    assert cli.get_command(None, 'init')
