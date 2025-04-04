from __future__ import annotations

import datetime
import json
import re
from functools import cached_property
from typing import Any

import requests_mock
from click.testing import CliRunner

from tests.fixture_data import (
    CONFIG_DATA,
    CONFIG_YAML,
    DEPLOYMENT_VERSION_DATA,
    EXECUTION_DATA,
    PIPELINE_DATA,
    PROJECT_DATA,
    YAML_WITH_EXTRACT_TRAIN_EVAL,
)
from valohai_cli import git
from valohai_cli.commands.execution.run import run
from valohai_cli.ctx import get_project
from valohai_cli.utils import get_random_string

ALTERNATIVE_YAML = "batch.yaml"


class RunAPIMock(requests_mock.Mocker):
    DEFAULT_DEPLOYMENT_VERSION_NAME = "220801.0"
    DEFAULT_COMMIT_ID = "f" * 16
    DEFAULT_PROJECT_ID = str(PROJECT_DATA["id"])

    def __init__(
        self,
        project_id: str = DEFAULT_PROJECT_ID,
        *,
        commit_id: str = DEFAULT_COMMIT_ID,
        deployment_id: str = "666",
        additional_payload_values: dict[str, Any] | None = None,
        deployment_version_name=DEFAULT_DEPLOYMENT_VERSION_NAME,
        expected_node_count=3,
        expected_edge_count=5,
        num_pipeline_parameters: int | None = None,
    ):
        super().__init__()
        self.expected_node_count = expected_node_count
        self.expected_edge_count = expected_edge_count
        self.last_create_execution_payload = None
        self.last_create_pipeline_payload = None
        self.project_id = project_id
        self.commit_id = commit_id
        self.deployment_id = deployment_id
        self.deployment_version_name = deployment_version_name
        self.additional_payload_values = additional_payload_values or {}
        self.num_pipeline_parameters = num_pipeline_parameters
        self.get(
            f"https://app.valohai.com/api/v0/projects/{project_id}/",
            json=self.handle_project,
        )
        self.get(
            f"https://app.valohai.com/api/v0/projects/{project_id}/commits/",
            json=self.handle_commits,
        )
        self.get(
            re.compile(r"^https://app.valohai.com/api/v0/commits/(?P<id>.+)/(?:\?.*)?$"),
            json=self.handle_commit_detail,
        )
        self.get(
            f"https://app.valohai.com/api/v0/commits/{commit_id}?include=config",
            json=self.handle_commit_detail,
        )
        self.get(
            re.compile(r"^https://app.valohai.com/api/v0/commits/(?:\?.*)$"),
            json=self.handle_commits_list,
        )
        self.get(
            re.compile(r"^https://app.valohai.com/api/v0/deployments/(?:\?.*)$"),
            json=self.handle_deployments_list,
        )
        self.get(
            f"https://app.valohai.com/api/v0/deployments/{self.deployment_id}/suggest_version_name/",
            json=self.handle_deployment_version_name_suggestion,
        )
        self.post(
            "https://app.valohai.com/api/v0/executions/",
            json=self.handle_create_execution,
        )
        self.post(
            "https://app.valohai.com/api/v0/deployment-versions/",
            json=self.handle_create_deployment_version,
        )
        self.post(
            "https://app.valohai.com/api/v0/pipelines/",
            json=self.handle_create_pipeline,
        )
        self.post(
            f"https://app.valohai.com/api/v0/projects/{project_id}/import-package/",
            json=self.handle_create_commit,
        )

    def handle_project(self, request, context):
        return {
            "id": self.project_id,
            "name": f"Project {self.project_id}",
            "yaml_path": "valohai.yaml",
        }

    def handle_deployments_list(self, request, context):
        return {
            "results": [
                {
                    "name": "main-deployment",
                    "id": self.deployment_id,
                },
            ],
        }

    def handle_deployment_version_name_suggestion(self, request, context):
        return {
            "name": self.deployment_version_name,
        }

    def handle_commits_list(self, request, context):
        return {
            "results": self.handle_commits(request, context),
        }

    def handle_commits(self, request, context):
        commit_obj = self.handle_commit_detail(request, context)
        commit_obj.pop("config", None)  # This wouldn't be in the list response
        return [commit_obj]

    def handle_commit_detail(self, request, context):
        return {
            "identifier": self.commit_id,
            "commit_time": datetime.datetime.now().isoformat(),
            "url": f"/api/v0/commits/{self.commit_id}/",
            "config": CONFIG_DATA,
        }

    def handle_create_execution(self, request, context):
        body_json = json.loads(request.body.decode("utf-8"))
        assert body_json["project"] == self.project_id
        assert body_json["step"] in ("Train model", "Batch feature extraction")
        assert body_json["commit"] == self.commit_id
        for key, expected_value in self.additional_payload_values.items():
            body_value = body_json[key]
            assert body_value == expected_value, f"body[{key}] = {body_value!r}, expected {expected_value!r}"
        context.status_code = 201
        self.last_create_execution_payload = body_json
        return EXECUTION_DATA.copy()

    def handle_create_deployment_version(self, request, context):
        body_json = json.loads(request.body.decode("utf-8"))
        assert body_json["name"] == self.deployment_version_name
        if body_json["endpoint_configurations"].get("greet"):
            assert body_json["endpoint_configurations"]["greet"]["enabled"]
        if body_json["endpoint_configurations"].get("predict-digit"):
            files = body_json["endpoint_configurations"]["predict-digit"]["files"]
            assert files.get("model")
        context.status_code = 201
        return DEPLOYMENT_VERSION_DATA.copy()

    def handle_create_pipeline(self, request, context):
        body_json = json.loads(request.body.decode("utf-8"))
        assert body_json["project"] == self.project_id
        assert len(body_json["edges"]) == self.expected_edge_count
        assert len(body_json["nodes"]) == self.expected_node_count
        if self.num_pipeline_parameters is not None:
            assert len(body_json["parameters"]) == self.num_pipeline_parameters
        context.status_code = 201
        self.last_create_pipeline_payload = body_json
        return PIPELINE_DATA.copy()

    def handle_create_commit(self, request, context):
        assert request.body
        commit_id = f"~{get_random_string()}"
        self.commit_id = commit_id  # Only accept the new commit
        return {
            "repository": "8",
            "identifier": commit_id,
            "ref": "adhoc",
            "ctime": "2017-03-09T14:56:53.875721Z",
            "commit_time": "2017-03-09T14:56:53.875475Z",
        }


class RunTestSetup:
    def __init__(
        self,
        *,
        monkeypatch,
        adhoc: bool,
        step_name: str = "train",
        config_yaml=CONFIG_YAML,
    ):
        self.adhoc = adhoc
        self.project_id = str(PROJECT_DATA["id"])
        self.commit_id = "f" * 40
        monkeypatch.setattr(git, "get_current_commit", lambda dir: self.commit_id)

        with open(get_project().get_config_filename(), "w") as yaml_fp:
            yaml_fp.write(config_yaml)

        # Create an alternative yaml as well (monorepo style)
        with open(get_project().get_config_filename(yaml_path=ALTERNATIVE_YAML), "w") as yaml_fp:
            yaml_fp.write(YAML_WITH_EXTRACT_TRAIN_EVAL)

        self.args = [step_name]
        if adhoc:
            self.args.insert(0, "--adhoc")
        self.values: dict[str, Any] = {}

    @cached_property
    def run_api_mock(self) -> RunAPIMock:
        return RunAPIMock(
            self.project_id,
            commit_id=self.commit_id,
            additional_payload_values=self.values,
        )

    def run(self, *, catch_exceptions=False, verify_adhoc=True) -> str:
        with self.run_api_mock:
            output = CliRunner().invoke(run, self.args, catch_exceptions=catch_exceptions).output
            if verify_adhoc:
                # Making sure that non-adhoc executions don't turn adhoc or vice versa.
                assert ("Uploaded ad-hoc code" in output) == self.adhoc
                assert f"#{EXECUTION_DATA['counter']}" in output
        return output
