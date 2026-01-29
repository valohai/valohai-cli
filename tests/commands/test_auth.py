import pytest
import requests_mock

from valohai_cli.commands.login import login
from valohai_cli.commands.logout import logout
from valohai_cli.settings import settings
from valohai_cli.utils import get_random_string


class AuthMock(requests_mock.Mocker):
    def __init__(self, username="john.smith", password="123456"):
        super().__init__()
        self.username = username
        self.password = password
        self.token = get_random_string()
        self.post("https://app.valohai.com/api/v0/get-token/", json=self.handle_get_token)
        self.get("https://app.valohai.com/api/v0/users/me/", json=self.handle_get_me)

    def handle_get_token(self, request, context):
        # Not perfect, but it'll do
        assert self.username in request.body
        assert self.password in request.body
        return {"token": self.token}

    def handle_get_me(self, request, context):
        # Not perfect either
        assert request.headers["Authorization"].endswith(self.token)
        return {"id": 1, "username": self.username}


@pytest.mark.parametrize("mode", ("param", "interactive"))
def test_auth(runner, mode):
    # Log in...
    with AuthMock() as m:
        if mode == "param":
            result = runner.invoke(
                login,
                [
                    "-h",
                    "https://app.valohai.com",
                    "-u",
                    m.username,
                    "-p",
                    m.password,
                ],
                catch_exceptions=False,
            )
        elif mode == "interactive":
            result = runner.invoke(
                login,
                input="\n".join([
                    "",  # accept default host
                    m.username,  # enter username
                    m.password,  # enter password
                ]),
            )
        assert "Logged in" in result.output
        assert settings.token == m.token

    # Attempting to re-login requires a confirmation, so this aborts.
    result = runner.invoke(login, ["-u", m.username, "-p", m.password], catch_exceptions=False)
    assert "Aborted!" in result.output

    # Log out...

    result = runner.invoke(logout, input="y", catch_exceptions=False)
    assert not settings.token

    # And again.

    assert "not logged in" in runner.invoke(logout).output
