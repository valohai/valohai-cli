import random
import uuid

LOGGED_IN_DATA = {
    "host": "https://app.valohai.com/",
    "user": {"id": "x"},
    "token": "x",
}

alias_id = str(uuid.uuid4())
commit_id = str(uuid.uuid4())
datum_id = str(uuid.uuid4())
deployment_id = str(uuid.uuid4())
deployment_version_id = str(uuid.uuid4())
environment_id = str(uuid.uuid4())
execution_id = str(uuid.uuid4())
notebook_execution_id = str(uuid.uuid4())
pipeline_id = str(uuid.uuid4())
project_id = str(uuid.uuid4())
task_id = str(uuid.uuid4())


PROJECT_DATA = {
    "id": project_id,
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
        "id": environment_id,
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
            "pipeline": pipeline_id,
            "source_key": "*train-images*",
            "source_node": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "source_type": "output",
            "target_key": "training-set-images",
            "target_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "target_type": "input",
        },
        {
            "id": "01744e18-c8e3-492d-135e-a1ef237c4a94",
            "pipeline": pipeline_id,
            "source_key": "*train-labels*",
            "source_node": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "source_type": "output",
            "target_key": "training-set-labels",
            "target_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "target_type": "input",
        },
        {
            "id": "01744e18-c8e6-e27d-442b-b820c8975a37",
            "pipeline": pipeline_id,
            "source_key": "*test-images*",
            "source_node": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "source_type": "output",
            "target_key": "test-set-images",
            "target_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "target_type": "input",
        },
        {
            "id": "01744e18-c8e9-924a-7f89-d4033b0bd1a4",
            "pipeline": pipeline_id,
            "source_key": "*test-labels*",
            "source_node": "01744e18-c8c1-a267-44a2-5e7f0a86bf38",
            "source_type": "output",
            "target_key": "test-set-labels",
            "target_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "target_type": "input",
        },
        {
            "id": "01744e18-c8ec-d09c-4e5e-c749fbbf1e80",
            "pipeline": pipeline_id,
            "source_key": "model*",
            "source_node": "01744e18-c8c7-a1d4-d0be-0cb3cbfa7ee0",
            "source_type": "output",
            "target_key": "model",
            "target_node": "01744e18-c8c9-167b-c2b6-a9f06d0c1735",
            "target_type": "input",
        },
    ],
    "id": pipeline_id,
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
            "pipeline": pipeline_id,
            "status": "created",
            "type": "execution",
        },
        {
            "execution": None,
            "id": "01744e18-c8c9-167b-c2b6-a9f06d0c1735",
            "log": [],
            "name": "evaluate",
            "pipeline": pipeline_id,
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
            "pipeline": pipeline_id,
            "status": "started",
            "type": "execution",
        },
    ],
    "project": PROJECT_DATA,
    "status": "started",
    "title": "Training Pipeline",
    "url": f"http://127.0.0.1:8000/api/v0/pipelines/{pipeline_id}/",
    "urls": {
        "display": f"http://127.0.0.1:8000/p/magda/tensorflow-example/pipeline/{pipeline_id}/",
    },
}

TASK_LIST_DATA = {
    "configuration": {"execution_count": 50, "maximum_queued_executions": 50},
    "counter": 2,
    "creator_name": "admin",
    "ctime": "2025-03-05T15:14:10.159699Z",
    "deleted": False,
    "id": task_id,
    "is_pinned": False,
    "mtime": "2025-03-05T15:14:10.159706Z",
    "n_children": 50,
    "n_comments": 0,
    "n_executions": 50,
    "project": project_id,
    "status": "started",
    "status_detail": None,
    "status_summary": {
        "count": 50,
        "created_count": 0,
        "queued_count": 47,
        "started_count": 0,
        "complete_count": 0,
        "error_count": 3,
        "stopping_count": 0,
        "stopping_hard_count": 0,
        "stopped_count": 0,
    },
    "tags": [],
    "title": "Training Task",
    "type": "distributed",
    "url": f"http://127.0.0.1:8000/api/v0/tasks/{task_id}/",
    "urls": {
        "copy": f"http://127.0.0.1:8000/p/magda/tensorflow-example/tasks/create/?from={task_id}",
        "display": f"http://127.0.0.1:8000/p/magda/tensorflow-example/task/{task_id}/",
        "executions": f"http://127.0.0.1:8000/api/v0/executions/?task={task_id}",
        "pipelines": f"http://127.0.0.1:8000/api/v0/pipelines/?task={task_id}",
        "property_keys": f"http://127.0.0.1:8000/api/v0/tasks/{task_id}/property-keys/",
        "stop": f"http://127.0.0.1:8000/api/v0/tasks/{task_id}/stop/",
    },
}

ENVIRONMENT_NESTED_DATA = {
    "allow_personal_usage": True,
    "bill_usage": True,
    "ctime": "2023-08-03T08:04:58.485822Z",
    "description": "",
    "enabled": True,
    "gpu_spec": "",
    "has_gpu": False,
    "id": environment_id,
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
    "url": f"http://127.0.0.1:8000/api/v0/environments/{environment_id}",
    "enable_smart_vm_selection": False,
    "supports_priority": False,
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
    "environment": ENVIRONMENT_NESTED_DATA,
    "id": notebook_execution_id,
    "is_pinned": False,
    "mtime": "2025-05-21T12:14:55.495446Z",
    "n_alerts": 0,
    "n_comments": 0,
    "n_outputs": 0,
    "parameters": {},
    "pipeline": None,
    "pipeline_counter": None,
    "project": {
        "id": project_id,
        "name": "great-notebook-success",
        "description": "",
        "owner": {
            "id": 42,
            "username": "data-science-inc",
        },
        "ctime": "2025-01-03T08:28:42.593000Z",
        "mtime": "2025-01-03T08:28:42.593021Z",
        "url": f"http://127.0.0.1:8000/api/v0/projects/{project_id}/",
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
        "copy": f"http://127.0.0.1:8000/p/data-science-inc/great-notebook-success/executions/create/?from={notebook_execution_id}",
        "copy_to_task": f"http://127.0.0.1:8000/p/data-science-inc/great-notebook-success/tasks/create/?from={notebook_execution_id}",
        "display": f"http://127.0.0.1:8000/p/data-science-inc/great-notebook-success/execution/{notebook_execution_id}/",
        "stop": f"http://127.0.0.1:8000/api/v0/executions/{notebook_execution_id}/stop/",
    },
    "url": f"http://127.0.0.1:8000/api/v0/executions/{notebook_execution_id}/",
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
