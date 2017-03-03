from uuid import uuid4

from valohai_cli.utils import get_random_string


def get_project_data(n_projects):
    return {
        'results': [
            {'id': str(uuid4()), 'name': get_random_string()}
            for i in range(n_projects)
        ],
    }
