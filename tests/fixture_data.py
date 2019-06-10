import random
import uuid

import yaml

LOGGED_IN_DATA = {
    'host': 'https://app.valohai.com/',
    'user': {'id': 'x'},
    'token': 'x',
}

PROJECT_DATA = {
    'id': '000',
    'name': 'nyan',
    'description': 'nyan',
    'owner': 1,
    'ctime': '2016-12-16T12:25:52.718310Z',
    'mtime': '2017-01-20T14:35:02.196871Z',
    'urls': {
        'display': 'https://app.valohai.com/p/nyan/nyan/',
    }
}

execution_id = str(uuid.uuid4())
datum_id = str(uuid.uuid4())

OUTPUT_DATUM_DATA = {
    "id": datum_id,
    "size": 509739,
    "ctime": "2019-05-23T14:26:35.604807Z",
    "file_ctime": "2019-05-23T14:26:33.607583Z",
    "file_mtime": "2019-05-23T14:26:33.607583Z",
    "name": "yvrw91fdvwz21.png",
    "output_execution": {
        "id": execution_id,
    },
}

EXECUTION_DATA = {
    'counter': random.randint(1, 100),
    'ctime': '2017-02-08T11:09:16.120102Z',
    'id': execution_id,
    'project': PROJECT_DATA,
    'commit': {
        'repository': 666,
        'identifier': '000',
        'ref': 'master',
        'commit_time': '2017-02-15T08:46:58Z',
        'url': 'https://app.valohai.com/api/v0/commits/7/'
    },
    'task': None,
    'duration': 777,
    'status': 'complete',
    'step': 'run training',
    'url': 'https://app.valohai.com/api/v0/executions/{id}/'.format(id=execution_id),
    'urls': {
        'copy': 'https://app.valohai.com/api/v0/executions/34/copy/',
        'display': 'https://app.valohai.com/p/test/mnist/execution/34/',
        'stop': 'https://app.valohai.com/api/v0/executions/34/stop/',
    },
    'parameters': {
        'dropout': 0.9,
        'learning_rate': 0.001,
        'max_steps': 300,
    },
    'outputs': [
        OUTPUT_DATUM_DATA,
    ],
    'environment': {
        'id': '88888888-8888-8888-8888-888888888888',
        'name': 'local',
        'owner': None,
        'unfinished_job_count': 0,
    },
    'cumulative_metadata': {
        'oispa': 'beer',
    },
}

OUTPUT_DATUM_RESPONSE_DATA = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [OUTPUT_DATUM_DATA],
}

OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA = {
    'url': 'https://example.com/{}'.format(str(uuid.uuid4())),
}

EVENT_RESPONSE_DATA = {
    'total': 5,
    'truncated': False,
    'events': [
        {
            'time': '2017-02-16T15:25:33.037000',
            'stream': 'status',
            'message': 'hOI!!! I\'m temmie!'
        },
        {
            'time': '2017-02-16T15:25:33.037000',
            'stream': 'stderr',
            'message': 'oh no',
        },
    ],
}

CONFIG_YAML = """
---

- step:
    name: Train model
    image: busybox
    command: "false"
    inputs:
      - name: in1
        default: http://example.com/
    parameters:
      - name: max_steps
        pass-as: --max_steps={v}
        description: Number of steps to run the trainer
        type: integer
        default: 300

"""

INVALID_CONFIG_YAML = """
---

- step:
    image: 8
    command:
      foo: 6
      bar: n
    outputs: yes
    parameters:
      - name: a
        type: integer
      - 38

"""

BROKEN_CONFIG_YAML = """'"""

CONFIG_DATA = yaml.safe_load(CONFIG_YAML)
