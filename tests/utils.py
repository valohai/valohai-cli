from uuid import uuid4

from valohai_cli.utils import get_random_string


def get_project_data(n_projects):
    return {
        'results': [
            {'id': str(uuid4()), 'name': get_random_string()}
            for i in range(n_projects)
        ],
    }


def make_call_stub(retval=None):
    calls = []

    def call_stub(*args, **kwargs):
        calls.append({'args': args, 'kwargs': kwargs})
        return retval

    call_stub.calls = calls
    return call_stub
