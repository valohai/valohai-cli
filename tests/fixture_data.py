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
    'url': f'https://app.valohai.com/api/v0/executions/{execution_id}/',
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

PIPELINE_DATA = {
    'counter': 21,
    'creator': {'id': 1, 'username': 'magda'},
    'ctime': '2020-09-02T09:14:41.216963Z',
    'deleted': False,
    'edges': [{'id': '01744e18-c8cf-4ed9-0a44-412f65b0f224',
               'pipeline': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
               'source_key': '*train-images*',
               'source_node': '01744e18-c8c1-a267-44a2-5e7f0a86bf38',
               'source_type': 'output',
               'target_key': 'training-set-images',
               'target_node': '01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0',
               'target_type': 'input'},
              {'id': '01744e18-c8e3-492d-135e-a1ef237c4a94',
               'pipeline': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
               'source_key': '*train-labels*',
               'source_node': '01744e18-c8c1-a267-44a2-5e7f0a86bf38',
               'source_type': 'output',
               'target_key': 'training-set-labels',
               'target_node': '01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0',
               'target_type': 'input'},
              {'id': '01744e18-c8e6-e27d-442b-b820c8975a37',
               'pipeline': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
               'source_key': '*test-images*',
               'source_node': '01744e18-c8c1-a267-44a2-5e7f0a86bf38',
               'source_type': 'output',
               'target_key': 'test-set-images',
               'target_node': '01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0',
               'target_type': 'input'},
              {'id': '01744e18-c8e9-924a-7f89-d4033b0bd1a4',
               'pipeline': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
               'source_key': '*test-labels*',
               'source_node': '01744e18-c8c1-a267-44a2-5e7f0a86bf38',
               'source_type': 'output',
               'target_key': 'test-set-labels',
               'target_node': '01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0',
               'target_type': 'input'},
              {'id': '01744e18-c8ec-d09c-4e5e-c749fbbf1e80',
               'pipeline': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
               'source_key': 'model*',
               'source_node': '01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0',
               'source_type': 'output',
               'target_key': 'model',
               'target_node': '01744e18-c8c9-167b-c2b6-a9f06d0c1735',
               'target_type': 'input'}],
    'id': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
    'log': [{'ctime': '2020-09-02T09:14:41.375499Z',
             'identifier': 'node_started',
             'kind': 'other',
             'message': 'Node "preprocess" started'},
            {'ctime': '2020-09-02T09:14:41.271304Z',
             'identifier': 'started',
             'kind': 'other',
             'message': 'Pipeline started'}],
    'nodes': [{'execution': None,
               'id': '01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0',
               'log': [],
               'name': 'train',
               'pipeline': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
               'status': 'created',
               'type': 'execution'},
              {'execution': None,
               'id': '01744e18-c8c9-167b-c2b6-a9f06d0c1735',
               'log': [],
               'name': 'evaluate',
               'pipeline': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
               'status': 'created',
               'type': 'execution'},
              {'execution': EXECUTION_DATA,
               'id': '01744e18-c8c1-a267-44a2-5e7f0a86bf38',
               'log': [{'ctime': '2020-09-02T09:14:41.372952Z',
                        'identifier': '',
                        'kind': 'other',
                        'message': 'Created execution tensorflow-example/#24'}],
               'name': 'preprocess',
               'pipeline': '01744e18-c8bf-e6cd-d329-5de7ed61bb52',
               'status': 'started',
               'type': 'execution'}],
    'project': PROJECT_DATA,
    'status': 'started',
    'title': 'Training Pipeline',
    'url': 'http://127.0.0.1:8000/api/v0/pipelines/01744e18-c8bf-e6cd-d329-5de7ed61bb52/',
    'urls': {
        'display': 'http://127.0.0.1:8000/p/magda/tensorflow-example/pipeline/01744e18-c8bf-e6cd-d329-5de7ed61bb52/'}
}

OUTPUT_DATUM_RESPONSE_DATA = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [OUTPUT_DATUM_DATA],
}

OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA = {
    'url': f'https://example.com/{str(uuid.uuid4())}',
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

PIPELINE_YAML = """
- step:
    name: Preprocess dataset (MNIST)
    image: tensorflow/tensorflow:1.13.1-gpu-py3
    command: python preprocess.py
    inputs:
      - name: training-set-images
        default: https://valohaidemo.blob.core.windows.net/mnist/train-images-idx3-ubyte.gz
      - name: training-set-labels
        default: https://valohaidemo.blob.core.windows.net/mnist/train-labels-idx1-ubyte.gz
      - name: test-set-images
        default: https://valohaidemo.blob.core.windows.net/mnist/t10k-images-idx3-ubyte.gz
      - name: test-set-labels
        default: https://valohaidemo.blob.core.windows.net/mnist/t10k-labels-idx1-ubyte.gz

- step:
    name: Train model (MNIST)
    image: tensorflow/tensorflow:1.13.1-gpu-py3
    command: python train.py {parameters}
    parameters:
      - name: max_steps
        pass-as: --max_steps={v}
        description: Number of steps to run the trainer
        type: integer
        default: 300
      - name: learning_rate
        pass-as: --learning_rate={v}
        description: Initial learning rate
        type: float
        default: 0.001
      - name: dropout
        pass-as: --dropout={v}
        description: Keep probability for training dropout
        type: float
        default: 0.9
      - name: batch_size
        pass-as: --batch_size={v}
        description: Training batch size (larger batches are usually more efficient on GPUs)
        type: integer
        default: 200
    inputs:
      - name: training-set-images
        default: https://valohaidemo.blob.core.windows.net/mnist/train-images-idx3-ubyte.gz
      - name: training-set-labels
        default: https://valohaidemo.blob.core.windows.net/mnist/train-labels-idx1-ubyte.gz
      - name: test-set-images
        default: https://valohaidemo.blob.core.windows.net/mnist/t10k-images-idx3-ubyte.gz
      - name: test-set-labels
        default: https://valohaidemo.blob.core.windows.net/mnist/t10k-labels-idx1-ubyte.gz

- step:
    name: Batch inference (MNIST)
    image: tensorflow/tensorflow:1.13.1-py3
    command:
      - pip install --disable-pip-version-check --quiet -r requirements.txt
      - python batch_inference.py --model-dir=/valohai/inputs/model/ --image-dir=/valohai/inputs/images
    inputs:
      - name: model
      - name: images
        default:
          - https://valohaidemo.blob.core.windows.net/mnist/four-inverted.png
          - https://valohaidemo.blob.core.windows.net/mnist/five-inverted.png
          - https://valohaidemo.blob.core.windows.net/mnist/five-normal.jpg

- step:
    name: Compare predictions (MNIST)
    image: tensorflow/tensorflow:1.13.1-py3
    command: python compare.py --prediction-dir=/valohai/inputs/predictions/
    inputs:
      - name: predictions

- step:
    name: Worker environment check
    image: tensorflow/tensorflow:1.13.1-gpu-py3
    command:
      - pwd
      - ls -la
      - nvidia-smi
      - python --version
      - nvcc --version | grep release

- pipeline:
    name: Training Pipeline
    nodes:
      - name: preprocess
        type: execution
        step: Preprocess dataset (MNIST)
      - name: train
        type: execution
        step: Train model (MNIST)
        override:
          inputs:
            - name: training-set-images
            - name: training-set-labels
            - name: test-set-images
            - name: test-set-labels
      - name: evaluate
        type: execution
        step: Batch inference (MNIST)
    edges:
      - [preprocess.output.*train-images*, train.input.training-set-images]
      - [preprocess.output.*train-labels*, train.input.training-set-labels]
      - [preprocess.output.*test-images*, train.input.test-set-images]
      - [preprocess.output.*test-labels*, train.input.test-set-labels]
      - [train.output.model*, evaluate.input.model]

- pipeline:
    name: Train Pipeline
    nodes:
      - name: preprocess
        type: execution
        step: Preprocess dataset (MNIST)
      - name: train
        type: execution
        step: Train model (MNIST)
        override:
          inputs:
            - name: training-set-images
            - name: training-set-labels
            - name: test-set-images
            - name: test-set-labels
      - name: evaluate
        type: execution
        step: Batch inference (MNIST)
    edges:
      - [preprocess.output.*train-images*, train.input.training-set-images]
      - [preprocess.output.*train-labels*, train.input.training-set-labels]
      - [preprocess.output.*test-images*, train.input.test-set-images]
      - [preprocess.output.*test-labels*, train.input.test-set-labels]
      - [train.output.model*, evaluate.input.model]
"""

YAML_WITH_EXTRACT_TRAIN_EVAL = """
- step:
    name: Batch feature extraction
    image: ubuntu:18.04
    command:
      - date > /valohai/outputs/aaa.md5
      - date > /valohai/outputs/bbb.sha256
- step:
    name: Train model
    image: ubuntu:18.04
    command:
      - find /valohai/inputs -type f -exec sha1sum '{}' ';' > /valohai/outputs/model.txt
    parameters:
      - name: learning_rate
        pass-as: --learning_rate={v}
        description: Initial learning rate
        type: float
        default: 0.001
    inputs:
      - name: aaa
      - name: bbb
- step:
    name: Evaluate
    image: ubuntu:18.04
    inputs:
      - name: models
    command:
      - ls -lar
"""

YAML_WITH_TRAIN_EVAL = """
- step:
    name: Train model
    image: ubuntu:18.04
    command:
      - find /valohai/inputs -type f -exec sha1sum '{}' ';' > /valohai/outputs/model.txt
    parameters:
      - name: learning_rate
        pass-as: --learning_rate={v}
        description: Initial learning rate
        type: float
        default: 0.001
    inputs:
      - name: aaa
      - name: bbb
- step:
    name: Evaluate
    image: ubuntu:18.04
    inputs:
      - name: models
    command:
      - ls -lar
"""

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
      - name: learning_rate
        type: float
        default: 0.1337
      - name: enable_mega_boost
        type: flag
    environment-variables:
      - name: testenvvar
        default: 'test'

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

PYTHON_SOURCE_USING_VALOHAI_UTILS = """
import os

import valohai

params = {
    "param1": True,
    "param2": "asdf",
    "param3": 123,
    "param4": 0.0001,
}

inputs = {"input1": "asdf", "input2": ["yolol", "yalala"]}


def prepare(a, b):
    print("this is fake method %s %s" % (a, b))


valohai.prepare(step="foobar1", parameters=params, inputs=inputs)
"""

PYTHON_SOURCE = """
import os

print("I'm just a poor boy without any utils.")
"""

PYTHON_SOURCE_DEFINING_PIPELINE = """
from valohai import Pipeline


def main(config) -> Pipeline:
    pipe = Pipeline(name="mypipeline", config=config)

    # Define nodes
    extract = pipe.execution("Batch feature extraction")
    train = pipe.task("Train model")
    evaluate = pipe.execution("Evaluate")

    # Configure training task node
    train.linear_parameter("learning_rate", min=0, max=1, step=0.1)

    # Configure pipeline
    extract.output("a*").to(train.input("aaa"))
    extract.output("a*").to(train.input("bbb"))
    train.output("*").to(evaluate.input("models"))

    return pipe
"""
