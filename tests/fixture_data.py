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
}

EXECUTION_DATA = {
    'counter': 7,
    'ctime': '2017-02-08T11:09:16.120102Z',
    'id': 34,
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
    'url': 'https://app.valohai.com/api/v0/executions/34/',
    'urls': {
        'copy': '/api/v0/executions/34/copy/',
        'display': '/p/test/mnist/execution/34/',
        'stop': '/api/v0/executions/34/stop/',
    },
    'events': [
        {
            'time': '2017-02-16T15:25:33.037000',
            'stream': 'status',
            'message': 'hOI!!! I\'m temmie!'
        },
    ],
    'parameters': {
        'dropout': 0.9,
        'learning_rate': 0.001,
        'max_steps': 300,
    },
    'outputs': [
        {
            'name': 'a.txt',
            'ctime': '2017-02-16T15:25:59.304888Z',
            'size': 120500,
            'url': 'http://filestash.example.com/foo/a.txt',
        },
        {
            'name': 'b.txt',
            'ctime': '2017-02-16T15:25:59.420535Z',
            'size': 25000,
            'url': 'http://filestash.example.com/foo/b.txt'
        },
    ],
    'environment': {
        'id': '88888888-8888-8888-8888-888888888888',
        'name': 'local',
        'owner': None,
        'unfinished_job_count': 0,
    },
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
