import random
import uuid

import yaml

LOGGED_IN_DATA = {
    "host": "https://app.valohai.com/",
    "user": {"id": "x"},
    "token": "x",
}

PROJECT_DATA = {
    "id": "000",
    "name": "nyan",
    "description": "nyan",
    "owner": 1,
    "ctime": "2016-12-16T12:25:52.718310Z",
    "mtime": "2017-01-20T14:35:02.196871Z",
    "urls": {
        "display": "https://app.valohai.com/p/nyan/nyan/",
    },
    "environment_variables": {
        "test1": {
            "value": "val1",
            "secret": False,
        },
        "ssshhh": {
            "value": None,
            "secret": True,
        },
    },
}

execution_id = str(uuid.uuid4())
datum_id = str(uuid.uuid4())
alias_id = str(uuid.uuid4())
commit_id = str(uuid.uuid4())
project_id = str(uuid.uuid4())
deployment_id = str(uuid.uuid4())
deployment_version_id = str(uuid.uuid4())

DATUM_DATA = {
    "id": datum_id,
    "size": 509739,
    "ctime": "2019-06-23T14:26:35.604807Z",
    "file_ctime": "2019-04-23T14:26:33.607583Z",
    "file_mtime": "2019-04-23T14:26:33.607583Z",
    "name": "image.png",
    "uri": "s4://my-bucket/data/1337/output",
    "output_execution": {
        "counter": 1337,
        "id": execution_id,
    },
}

DATUM_ALIAS_DATA = {
    "id": alias_id,
    "ctime": "2020-05-23T14:26:35.604807Z",
    "mtime": "2022-05-23T14:26:35.604807Z",
    "name": "this-is-alias-for-latest-png",
    "datum": DATUM_DATA,
}

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

DEPLOYMENT_VERSION_DATA = {
    "commit": {
        "adhoc": False,
        "commit_time": "2022-05-20T10:28:12Z",
        "description": "",
        "identifier": commit_id,
        "project_id": project_id,
        "ref": "master",
        "ref_names": [
            "master",
        ],
        "yaml_path": "valohai.yaml",
        "urls": {
            "display": f"https://app.valohai.com/p/magda/tensorflow-example/commits/{commit_id}/",
        },
        "has_config": True,
    },
    "ctime": "2022-07-15T11:50:43.645158Z",
    "mtime": "2022-07-15T11:50:43.645178Z",
    "deployment": deployment_id,
    "effective_enabled": True,
    "enabled": True,
    "id": deployment_version_id,
    "name": "20220715.0",
    "url": f"https://app.valohai.com/api/v0/deployment-versions/{deployment_version_id}/",
    "endpoints": [],
    "endpoint_urls": {},
    "environment_variables": {},
    "creator": {
        "id": 1,
        "username": "magda",
    },
    "urls": {
        "display": f"https://app.valohai.com/p/magda/tensorflow-example/deployment/{deployment_id}/#/version/{deployment_version_id}",
    },
}

EXECUTION_DETAIL_DATA = {
    "counter": random.randint(1, 100),
    "ctime": "2017-02-08T11:09:16.120102Z",
    "id": execution_id,
    "project": PROJECT_DATA,
    "commit": {
        "repository": 666,
        "identifier": "000",
        "ref": "master",
        "commit_time": "2017-02-15T08:46:58Z",
        "url": "https://app.valohai.com/api/v0/commits/7/",
    },
    "task": None,
    "duration": 777,
    "status": "complete",
    "step": "run training",
    "url": f"https://app.valohai.com/api/v0/executions/{execution_id}/",
    "urls": {
        "copy": "https://app.valohai.com/api/v0/executions/34/copy/",
        "display": "https://app.valohai.com/p/test/mnist/execution/34/",
        "stop": "https://app.valohai.com/api/v0/executions/34/stop/",
    },
    "parameters": {
        "dropout": 0.9,
        "learning_rate": 0.001,
        "max_steps": 300,
    },
    "outputs": [
        OUTPUT_DATUM_DATA,
    ],
    "environment": {
        "id": "88888888-8888-8888-8888-888888888888",
        "name": "local",
        "owner": None,
        "unfinished_job_count": 0,
    },
    "cumulative_metadata": {
        "oispa": "beer",
    },
}

PIPELINE_DATA = {
    "counter": 21,
    "creator": {"id": 1, "username": "magda"},
    "ctime": "2020-09-02T09:14:41.216963Z",
    "deleted": False,
    "edges": [
        {
            "id": "01744e18-c8cf-4ed9-0a44-412f65b0f224",
            "pipeline": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
            "source_key": "*train-images*",
            "source_node": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "source_type": "output",
            "target_key": "training-set-images",
            "target_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "target_type": "input",
        },
        {
            "id": "01744e18-c8e3-492d-135e-a1ef237c4a94",
            "pipeline": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
            "source_key": "*train-labels*",
            "source_node": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "source_type": "output",
            "target_key": "training-set-labels",
            "target_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "target_type": "input",
        },
        {
            "id": "01744e18-c8e6-e27d-442b-b820c8975a37",
            "pipeline": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
            "source_key": "*test-images*",
            "source_node": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "source_type": "output",
            "target_key": "test-set-images",
            "target_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "target_type": "input",
        },
        {
            "id": "01744e18-c8e9-924a-7f89-d4033b0bd1a4",
            "pipeline": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
            "source_key": "*test-labels*",
            "source_node": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "source_type": "output",
            "target_key": "test-set-labels",
            "target_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "target_type": "input",
        },
        {
            "id": "01744e18-c8ec-d09c-4e5e-c749fbbf1e80",
            "pipeline": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
            "source_key": "model*",
            "source_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "source_type": "output",
            "target_key": "model",
            "target_node": "01744e18-c8c9-167b-c2b6-a9f06d0c1735",
            "target_type": "input",
        },
    ],
    "id": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
    "log": [
        {
            "ctime": "2020-09-02T09:14:41.375499Z",
            "identifier": "node_started",
            "kind": "other",
            "message": 'Node "preprocess" started',
        },
        {
            "ctime": "2020-09-02T09:14:41.271304Z",
            "identifier": "started",
            "kind": "other",
            "message": "Pipeline started",
        },
    ],
    "nodes": [
        {
            "execution": None,
            "id": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "log": [],
            "name": "train",
            "pipeline": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
            "status": "created",
            "type": "execution",
        },
        {
            "execution": None,
            "id": "01744e18-c8c9-167b-c2b6-a9f06d0c1735",
            "log": [],
            "name": "evaluate",
            "pipeline": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
            "status": "created",
            "type": "execution",
        },
        {
            "execution": EXECUTION_DETAIL_DATA,
            "id": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "log": [
                {
                    "ctime": "2020-09-02T09:14:41.372952Z",
                    "identifier": "",
                    "kind": "other",
                    "message": "Created execution tensorflow-example/#24",
                },
            ],
            "name": "preprocess",
            "pipeline": "01744e18-c8bf-e6cd-d329-5de7ed61bb52",
            "status": "started",
            "type": "execution",
        },
    ],
    "project": PROJECT_DATA,
    "status": "started",
    "title": "Training Pipeline",
    "url": "http://127.0.0.1:8000/api/v0/pipelines/01744e18-c8bf-e6cd-d329-5de7ed61bb52/",
    "urls": {
        "display": "http://127.0.0.1:8000/p/magda/tensorflow-example/pipeline/01744e18-c8bf-e6cd-d329-5de7ed61bb52/",
    },
}

NOTEBOOK_EXECUTION_DATA: dict = {
    "commit": None,
    "counter": 11,
    "creator_id": "1",
    "creator_name": "notebook-user",
    "ctime": "2025-05-21T12:14:55.456659Z",
    "cumulative_metadata": None,
    "deleted": False,
    "duration": None,
    "end_time": None,
    "environment": {
        "allow_personal_usage": True,
        "bill_usage": True,
        "ctime": "2023-08-03T08:04:58.485822Z",
        "description": "",
        "enabled": True,
        "gpu_spec": "",
        "has_gpu": False,
        "id": "0189ba6d-b1f5-4b64-1a08-9ff09f447033",
        "is_scalable": False,
        "mtime": "2023-08-03T08:04:58.485828Z",
        "name": "The Default Environment",
        "owner": None,
        "per_hour_price_usd": "0.00000",
        "per_user_queue_quota": 0,
        "per_user_resource_quotas": None,
        "provider": None,
        "scale_down_grace_period": 15,
        "scale_max": 100,
        "scale_min": 0,
        "slug": "default",
        "spot": False,
        "spot_max_price": 0.0,
        "type": "vm",
        "url": "http://127.0.0.1:8000/api/v0/environments/0189ba6d-b1f5-4b64-1a08-9ff09f447033/",
        "enable_smart_vm_selection": False,
        "supports_priority": False,
    },
    "id": "0196f2c4-a3aa-05c6-802a-209b7b8802d8",
    "is_pinned": False,
    "mtime": "2025-05-21T12:14:55.495446Z",
    "n_alerts": 0,
    "n_comments": 0,
    "n_outputs": 0,
    "parameters": {},
    "pipeline": None,
    "pipeline_counter": None,
    "project": {
        "id": "01942b47-f0d8-0021-c074-87370badadee",
        "name": "great-notebook-success",
        "description": "",
        "owner": {
            "id": 42,
            "username": "data-science-inc",
        },
        "ctime": "2025-01-03T08:28:42.593000Z",
        "mtime": "2025-01-03T08:28:42.593021Z",
        "url": "http://127.0.0.1:8000/api/v0/projects/01942b47-f0d8-0021-c074-87370badadee/",
        "urls": {
            "display": "http://127.0.0.1:8000/p/data-science-inc/great-notebook-success/",
            "display_repository": "http://127.0.0.1:8000/p/data-science-inc/great-notebook-success/settings/repository/",
        },
        "read_only": False,
    },
    "status": "queued",
    "status_detail": None,
    "step": "Notebook Execution",
    "step_icon": None,
    "tags": [],
    "task_tags": [],
    "task": None,
    "task_counter": None,
    "title": "",
    "urls": {
        "copy": "http://127.0.0.1:8000/p/data-science-inc/great-notebook-success/executions/create/?from=0196f2c4-a3aa-05c6-802a-209b7b8802d8",
        "copy_to_task": "http://127.0.0.1:8000/p/data-science-inc/great-notebook-success/tasks/create/?from=0196f2c4-a3aa-05c6-802a-209b7b8802d8",
        "display": "http://127.0.0.1:8000/p/data-science-inc/great-notebook-success/execution/0196f2c4-a3aa-05c6-802a-209b7b8802d8/",
        "stop": "http://127.0.0.1:8000/api/v0/executions/0196f2c4-a3aa-05c6-802a-209b7b8802d8/stop/",
    },
    "url": "http://127.0.0.1:8000/api/v0/executions/0196f2c4-a3aa-05c6-802a-209b7b8802d8/",
    "pipeline_tags": [],
    "priority": 0,
    "command": "vhnb-boot --server-addr nb.valohai.dev",
    "environment_variables": {},
    "runtime_config": {
        "autorestart": False,
        "no_output_timeout": 604800,
    },
    "executor_identity": "",
    "image": "python:3.13",
    "inputs": [],
    "interpolated_command": "vhnb-boot --server-addr nb.valohai.dev",
    "price": 0.0,
    "stop_expression": "",
    "emissions": None,
    "parameter_categories": None,
}

OUTPUT_DATUM_RESPONSE_DATA = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [OUTPUT_DATUM_DATA],
}

OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA = {
    "url": f"https://example.com/{str(uuid.uuid4())}",
}

EVENT_RESPONSE_DATA = {
    "total": 5,
    "truncated": False,
    "events": [
        {
            "time": "2017-02-16T15:25:33.037000",
            "stream": "status",
            "message": "hOI!!! I'm temmie!",
        },
        {
            "time": "2017-02-16T15:25:33.037000",
            "stream": "stderr",
            "message": "oh no",
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
      - name: learning_rate
        type: float
        default: 0.1337
      - name: enable_mega_boost
        type: flag
      - name: multi-parameter
        default: ["one","two","three"]
        type: string
        multiple: separate
    environment-variables:
      - name: testenvvar
        default: 'test'
- endpoint:
    name: greet
    image: python:3.9
    port: 8000
    server-command: python -m wsgiref.simple_server
- endpoint:
    name: predict-digit
    description: predict digits from image inputs ("file" parameter)
    image: tensorflow/tensorflow:2.6.0
    wsgi: predict:predict
    files:
      - name: model
        description: Model output file from TensorFlow
        path: model.h5
"""

PIPELINE_YAML = (
    CONFIG_YAML
    + """
- step:
    name: Preprocess dataset (MNIST)
    image: tensorflow/tensorflow:1.13.1-gpu-py3
    command: python preprocess.py
    parameters:
      - name: sources
        type: string
        multiple: separate
        multiple-separator: '-'
        default:
        - port
        - railyard
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
    parameters:
      - name: pipeline_max_steps
        default: 1000
        targets:
            - Train model (MNIST).parameters.max_steps

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
    parameters:
      - name: pipeline_max_steps
        default: 1000
        targets:
            - Train model (MNIST).parameters.max_steps
      - name: sources
        default: [airport]
        targets:
            - preprocess.parameters.sources
"""
)

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

CONFIG_DATA = yaml.safe_load(PIPELINE_YAML)

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

KUBE_RESOURCE_YAML = """
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
      - name: multi-parameter
        default: ["one","two","three"]
        type: string
        multiple: separate
    environment-variables:
      - name: testenvvar
        default: 'test'
    resources:
      cpu:
        min: 1.0
        max: 2
      memory:
        min: 3
        max: 4
      devices:
        nvidia.com/gpu: 1
- endpoint:
    name: greet
    image: python:3.9
    port: 8000
    server-command: python -m wsgiref.simple_server
- endpoint:
    name: predict-digit
    description: predict digits from image inputs ("file" parameter)
    image: tensorflow/tensorflow:2.6.0
    wsgi: predict:predict
    files:
      - name: model
        description: Model output file from TensorFlow
        path: model.h5
"""

CACHE_VOLUME_YAML = """
---

- step:
    name: Train model
    image: busybox
    command: "false"
    cache-volumes:
      - default-cache-pvc
      - another-cache-pvc
"""

STATUS_EVENT_RESPONSE_DATA = {
    "total": 2,
    "status_events": [
        {
            "stream": "status",
            "message": '::ssh::{"port": 2222, "address": "127.0.0.1"}',
            "time": "2024-09-04T12:16:20.722000",
        },
        {
            "stream": "status",
            "message": "   $ ssh -i <path-to-private-key> 127.0.0.1 -p 2222 -t /bin/bash",
            "time": "2024-09-04T12:16:20.723000",
        },
    ],
}

PIPELINE_WITH_TASK_EXAMPLE = """
- step:
    name: preprocess
    image: python:3.7
    command:
      - python ./preprocess.py
- step:
    name: train
    image: python:3.7
    command:
      - pip install valohai-utils
      - python ./train.py {parameters}
    parameters:
      - name: id
        type: string
- pipeline:
    name: dynamic-task
    nodes:
      - name: preprocess
        step: preprocess
        type: execution
      - name: train-with-errors
        step: train
        type: task
        on-error: "continue"
      - name: train-optional
        step: train
        type: task
        on-error: "stop-next"
      - name: train-critical
        step: train
        type: task
        on-error: "stop-all"
    edges:
      - [preprocess.metadata.storeids, train-critical.parameter.id]
      - [preprocess.metadata.storeids, train-optional.parameter.id]
      - [preprocess.metadata.storeids, train-with-errors.parameter.id]
"""
