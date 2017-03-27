from uuid import uuid4

import requests_mock

from tests.utils import get_project_data


def get_project_mock(create_project_name=None, existing_projects=None):
    m = requests_mock.mock()
    if isinstance(existing_projects, int):
        existing_projects = get_project_data(existing_projects)
    if existing_projects is not None:
        m.get('https://app.valohai.com/api/v0/projects/', json=existing_projects)
    if create_project_name:
        m.post('https://app.valohai.com/api/v0/projects/', json=lambda request, context: {
            'id': str(uuid4()),
            'name': create_project_name,
        })
    return m
