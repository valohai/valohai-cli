from valohai_cli.commands.init import init


def test_init(runner):
    result = runner.invoke(init)
    assert result.exit_code == 0
    assert result.output == 'hello\n'
