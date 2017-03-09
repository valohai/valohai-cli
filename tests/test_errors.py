import pytest
import requests_mock

from valohai_cli.api import request
from valohai_cli.exceptions import APIError


def test_api_error(logged_in, capsys):
    with requests_mock.mock() as m:
        m.get('https://app.valohai.com/api/foo/', json={'error': 'Oh no!'}, status_code=406)
        with pytest.raises(APIError) as aei:
            request('get', 'https://app.valohai.com/api/foo/')
        aei.value.show()
        out, err = capsys.readouterr()
        assert err.startswith('Error: {"error": "Oh no!"}')
