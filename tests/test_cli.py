from valohai_cli.cli import cli


def test_command_enumeration():
    assert 'init' in cli.list_commands(None)
    assert cli.get_command(None, 'init')


def test_recursive_command_list(runner):
    output = runner.invoke(cli).output
    assert 'Commands' in output
    assert 'init' in output
    assert 'Commands (execution' in output
    assert 'execution info' in output
    assert 'execution watch' in output
    assert 'execution outputs' in output


def test_prefix_match(runner):
    output = runner.invoke(cli, ['exec']).output
    # Matched by prefix, mapped to `execution`'s help
    assert 'cli execution' in output


def test_ambiguous_match(runner):
    output = runner.invoke(cli, ['log']).output
    assert 'be more specific' in output
    assert 'login, logout' in output
