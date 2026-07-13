from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from valohai_yaml.objs import Step
from valohai_yaml.objs.task import Task

from valohai_cli.api import request
from valohai_cli.commands.execution.run.dynamic_run_command import RunCommand
from valohai_cli.exceptions import APIError
from valohai_cli.messages import success
from valohai_cli.models.project import Project
from valohai_cli.utils import sanitize_option_name

# Map YAML-style hyphenated on_child_error values to the API's underscored enum.
_ON_CHILD_ERROR_API_MAP = {
    "continue-and-complete": "continue_and_complete",
    "continue-and-error": "continue_and_error",
    "stop-all-and-error": "stop_all_and_error",
}

_TASK_CONFIGURATION_FIELDS = (
    "execution_count",
    "execution_batch_size",
    "optimization_target_metric",
    "optimization_target_value",
    "engine",
)


def _build_variant_parameters(task: Task, cli_parameters: dict[str, Any]) -> dict[str, Any]:
    """Build the variant parameters dict from the task blueprint and CLI overrides."""
    variant_parameters: dict[str, Any] = {}

    for vp in task.parameters:
        variant_parameters[vp.name] = {
            "style": vp.style.value,
            "rules": dict(vp.rules),
        }

    if task.parameter_sets:
        collected: dict[str, list[Any]] = {}
        for param_set in task.parameter_sets:
            for param_name, param_value in param_set.items():
                collected.setdefault(param_name, []).append(param_value)
        for param_name, items in collected.items():
            variant_parameters[param_name] = {"style": "multiple", "rules": {"items": items}}

    # CLI-provided parameter values become "single" style variants
    for name, value in cli_parameters.items():
        if name not in variant_parameters:
            variant_parameters[name] = {"style": "single", "rules": {"value": value}}

    return variant_parameters


def _build_task_configuration(task: Task) -> dict[str, Any]:
    """Build the configuration block from task blueprint fields."""
    configuration: dict[str, Any] = {}
    for field in _TASK_CONFIGURATION_FIELDS:
        value = getattr(task, field, None)
        if value is not None:
            configuration[field] = value
    return configuration


def _resolve_on_child_error(override: str | None, task: Task) -> str | None:
    """Resolve on_child_error from CLI override or task blueprint, mapped to API format."""
    on_child_error = override
    if on_child_error is None and task.on_child_error is not None:
        on_child_error = task.on_child_error.value
    if on_child_error:
        return _ON_CHILD_ERROR_API_MAP.get(on_child_error, on_child_error)
    return None


class TaskRunCommand(RunCommand):
    """
    A dynamically-generated subcommand for running a task.

    Extends RunCommand (which builds Click options from step parameters/inputs)
    and adds the task-specific payload fields (type, variant_parameters, configuration, etc.).
    """

    def __init__(
        self,
        project: Project,
        step: Step,
        task: Task,
        commit: str,
        environment: str | None = None,
        image: str | None = None,
        title: str | None = None,
        environment_variables: dict[str, str] | None = None,
        tags: Sequence[str] | None = None,
        max_queued: int | None = None,
        on_child_error: str | None = None,
    ) -> None:
        self.task = task
        self.max_queued = max_queued
        self.on_child_error_override = on_child_error
        super().__init__(
            project=project,
            step=step,
            commit=commit,
            environment=environment,
            image=image,
            title=title,
            environment_variables=environment_variables,
            tags=tags,
        )
        # Override the command name to use the task name
        self.name = sanitize_option_name(task.name.lower())

    def execute(self, **kwargs: Any) -> None:
        """Build the task payload and POST to the tasks API."""
        payload = self._build_task_payload(**kwargs)

        resp = request(
            method="post",
            url="/api/v0/tasks/",
            json=payload,
            api_error_class=TaskCreationAPIError,
        ).json()
        success(f"Task !{resp['counter']} created. See {resp['urls']['display']}")

    def _build_task_payload(self, **kwargs: Any) -> dict[str, Any]:
        _options, parameters, inputs = self._sift_kwargs(kwargs)
        task = self.task

        payload: dict[str, Any] = {
            "commit": self.commit,
            "project": self.project.id,
            "step": self.step.name,
            "type": task.type.value,
        }

        variant_parameters = _build_variant_parameters(task, parameters)
        if variant_parameters:
            payload["parameters"] = variant_parameters
        if inputs:
            payload["inputs"] = inputs

        configuration = _build_task_configuration(task)
        if configuration:
            payload["configuration"] = configuration

        max_queued = self.max_queued if self.max_queued is not None else task.maximum_queued_executions
        if max_queued is not None:
            payload["maximum_queued_executions"] = max_queued

        on_child_error = _resolve_on_child_error(self.on_child_error_override, task)
        if on_child_error:
            payload["on_child_error"] = on_child_error

        if task.stop_condition:
            payload["task_stop_expression"] = task.stop_condition
        if task.reuse_children:
            payload["allow_reuse"] = True

        for field in ("environment", "image", "title", "environment_variables", "tags"):
            payload.update(self._optional_item(field))

        return payload


class TaskCreationAPIError(APIError):
    pass
