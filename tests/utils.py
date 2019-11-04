from uuid import uuid4

from valohai_cli.utils import get_random_string


def get_project_list_data(n_projects):
    return {
        'results': [
            {
                "id": str(uuid4()),
                "name": get_random_string(),
                "description": str(i),
                "owner": {
                    "id": 1,
                    "username": "test"
                },
                "ctime": "2019-02-26T16:03:46.607917Z",
                "mtime": "2019-02-26T16:03:46.607938Z",
                "url": "...",
                "urls": {
                    "display": "...",
                    "display_repository": "..."
                },
                "execution_count": 1,
                "running_execution_count": 0,
                "queued_execution_count": 0,
                "last_execution_ctime": "2019-02-26T16:14:08.442080Z"
            }
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
