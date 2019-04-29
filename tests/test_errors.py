import pytest
import requests_mock
from click._compat import strip_ansi

from valohai_cli.api import request
from valohai_cli.exceptions import APIError
from valohai_cli.utils import get_random_string
from valohai_cli.utils.error_fmt import format_error_data


def test_api_error(logged_in, capsys):
    nonce = get_random_string()
    message = 'Oh no! ' + nonce
    with requests_mock.mock() as m:
        m.get('https://app.valohai.com/api/foo/', json={'error': message}, status_code=406)
        with pytest.raises(APIError) as aei:
            request('get', 'https://app.valohai.com/api/foo/')
        aei.value.show()
        out, err = capsys.readouterr()
        assert message in err


def test_error_formatter_simple():
    assert strip_ansi(format_error_data({
        "environment": [{"message": "Object with slug or primary key bluup does not exist.", "code": "does_not_exist"}]
    })) == 'environment:\n  * Object with slug or primary key bluup does not exist. (code: does_not_exist)'


def test_error_formatter_mixed():
    assert strip_ansi(format_error_data({
        "environment": [{"message": "Object with slug or primary key bluup does not exist.", "code": "does_not_exist"}],
        "non_field_errors": [
            'oh',
            'oh no',
            'that\'s bad',
            {'message': 'this is fine', 'code': 'dog_not_on_fire'},
        ],
    })) == ('''
* oh
* oh no
* that's bad
* this is fine (code: dog_not_on_fire)
environment:
  * Object with slug or primary key bluup does not exist. (code: does_not_exist)
    ''').strip()
