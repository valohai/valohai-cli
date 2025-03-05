from uuid import uuid4

from valohai_cli.ctx import get_project


def get_project_list_data(project_names):
    return {
        "results": [
            {
                "id": str(uuid4()),
                "name": name,
                "description": name,
                "owner": {
                    "id": 1,
                    "username": "test",
                },
                "ctime": "2019-02-26T16:03:46.607917Z",
                "mtime": "2019-02-26T16:03:46.607938Z",
                "url": "...",
                "urls": {
                    "display": "...",
                    "display_repository": "...",
                },
                "execution_count": 1,
                "running_execution_count": 0,
                "queued_execution_count": 0,
                "last_execution_ctime": "2019-02-26T16:14:08.442080Z",
            }
            for name in project_names
        ],
    }


def make_call_stub(retval=None):
    calls = []

    def call_stub(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return retval

    call_stub.calls = calls
    return call_stub


def write_yaml_config(yaml_content: str, yaml_path=None) -> None:
    project = get_project()
    config_filename = project.get_config_filename(yaml_path=yaml_path)
    with open(config_filename, "w") as yaml_fp:
        yaml_fp.write(yaml_content)
