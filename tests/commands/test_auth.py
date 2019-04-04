import requests_mock

from valohai_cli.commands.login import login
from valohai_cli.commands.logout import logout
from valohai_cli.settings import settings


def test_auth(runner):
    # Log in...
    with requests_mock.mock() as m:
        m.post('https://app.valohai.com/api/v0/get-token/', json={'token': 'X' * 40})
        m.get('https://app.valohai.com/api/v0/users/me/', json={'id': 1, 'username': 'john.smith'})
        result = runner.invoke(login, [
            '-u', 'john.smith',
            '-p', '123456',
        ])
        assert 'Logged in' in result.output
        assert settings.token == 'X' * 40

    # Attempting to re-login requires a confirmation, so this aborts.
    result = runner.invoke(login, ['-u', 'john.smith', '-p', '123456'], catch_exceptions=False)
    assert 'Aborted!' in result.output

    # Log out...

    result = runner.invoke(logout, input='y', catch_exceptions=False)
    assert not settings.token

    # And again.

    assert 'not logged in' in runner.invoke(logout).output
