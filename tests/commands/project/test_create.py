from uuid import uuid4

import pytest
import requests_mock

from valohai_cli.commands.project.create import create
from valohai_cli.utils import get_random_string


@pytest.mark.parametrize('link', (False, True))
def test_create(runner, logged_in, link):
    name = get_random_string()
    with requests_mock.mock() as m:
        m.post('https://app.valohai.com/api/v0/projects/', json={
            'id': str(uuid4()),
            'name': name,
        })
        result = runner.invoke(create, ['-n', name, ('--link' if link else '--no-link')])
        assert ('%s created' % name) in result.output
        if link:
            assert 'Linked' in result.output


@pytest.mark.parametrize('input', ('y', 'n'))
def test_create_linked(runner, logged_in_and_linked, input):
    name = get_random_string()
    with requests_mock.mock() as m:
        m.post('https://app.valohai.com/api/v0/projects/', json={
            'id': str(uuid4()),
            'name': name,
        })
        result = runner.invoke(create, ['-n', name], input=input)
        if input == 'y':
            assert ('%s created' % name) in result.output
            assert 'Linked' in result.output
