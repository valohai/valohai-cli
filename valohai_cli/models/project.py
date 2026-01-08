from __future__ import annotations

import io
import os
from typing import TextIO

import valohai_yaml
from click import BadParameter
from valohai_yaml.objs.config import Config

from valohai_cli.api import request
from valohai_cli.exceptions import APIError, InvalidConfig, NoExecution, NoPipeline, NoSuchEntity, NoTask
from valohai_cli.git import get_file_at_commit


def resolve_counter(counter: int | str) -> str:
    if isinstance(counter, str):
        counter = counter.lstrip("=#!")
        if not (counter.isdigit() or counter == "latest"):
            raise BadParameter(
                f'{counter} is not a valid counter value; it must be an integer or "latest"',
            )
    return str(counter)


class Project:
    is_remote = False

    def __init__(self, data: dict, directory: str) -> None:
        self.data = data
        if not os.path.isdir(directory):
            raise ValueError(f"Invalid directory: {directory}")
        self.directory = directory
        self._commit_list: list[dict] | None = None

    @property
    def id(self) -> str:
        return str(self.data["id"])

    @property
    def name(self) -> str:
        return str(self.data["name"])

    def get_config(self, commit_identifier: str | None = None, yaml_path: str | None = None) -> Config:
        """
        Get the `valohai_yaml.Config` object from the current working directory,
        or a given commit.

        :param commit_identifier: Hexadecimal commit identifier; optional.
        :param yaml_path: Override of the project's `yaml_path`; optional.
        :return: valohai_yaml.Config
        """
        yaml_path = yaml_path or self.get_yaml_path()
        if not commit_identifier:  # Current working directory
            filename = self.get_config_filename(yaml_path=yaml_path)
            with open(filename) as infp:
                return self._parse_config(infp, filename)
        else:  # Arbitrary commit
            filename = f"{commit_identifier}:{yaml_path}"
            directory = self.directory
            config_bytes = get_file_at_commit(directory, commit_identifier, yaml_path)
            config_sio = io.StringIO(config_bytes.decode("utf-8"))
            return self._parse_config(config_sio, filename)

    def _parse_config(self, config_fp: TextIO, filename: str = "<config file>") -> Config:
        try:
            return valohai_yaml.parse(config_fp)
        except OSError as err:
            raise InvalidConfig(f"Could not read {filename}") from err
        except valohai_yaml.ValidationErrors as ves:
            raise InvalidConfig(f"{filename} is invalid ({len(ves.errors)} errors); see `vh lint`")

    def get_config_filename(self, yaml_path: str | None = None) -> str:
        used_yaml_path = yaml_path or self.get_yaml_path()
        return os.path.join(self.directory, used_yaml_path)

    def get_yaml_path(self) -> str:
        # Make sure the older API versions that don't expose yaml_path don't completely break
        return self.data.get("yaml_path") or "valohai.yaml"

    def _get_object_from_counter(
        self,
        *,
        url_part: str,
        noun: str,
        exc_type: type[NoSuchEntity],
        counter: int | str,
        params: dict | None = None,
    ) -> dict:
        counter = resolve_counter(counter)
        try:
            data = request(
                method="get",
                url=f"/api/v0/{url_part}/{self.id}:{counter}/",
                params=(params or {}),
            ).json()
            assert isinstance(data, dict)
            return data
        except APIError as ae:
            if ae.response.status_code == 404:
                raise exc_type(f"{noun}{counter} does not exist")
            raise

    def get_execution_from_counter(self, counter: int | str, params: dict | None = None) -> dict:
        return self._get_object_from_counter(
            url_part="executions",
            noun="Execution #",
            exc_type=NoExecution,
            counter=counter,
            params=params,
        )

    def get_pipeline_from_counter(self, counter: int | str, params: dict | None = None) -> dict:
        return self._get_object_from_counter(
            url_part="pipelines",
            noun="Pipeline =",
            exc_type=NoPipeline,
            counter=counter,
            params=params,
        )

    def get_task_from_counter(self, counter: int | str, params: dict | None = None) -> dict:
        return self._get_object_from_counter(
            url_part="tasks",
            noun="Task !",
            exc_type=NoTask,
            counter=counter,
            params=params,
        )

    def load_commit_list(self) -> list[dict]:
        """
        Get a list of non-adhoc commits, newest first.
        """
        if self._commit_list is None:
            commits: list[dict] = list(
                request(
                    method="get",
                    url="/api/v0/commits/",
                    params={
                        "project": self.id,
                        "adhoc": "false",
                        "limit": 9000,
                    },
                ).json()["results"],
            )
            commits.sort(key=lambda c: str(c["commit_time"]), reverse=True)
            self._commit_list = commits
        return self._commit_list

    def resolve_commits(self, commit_identifier: str | None = None) -> list[dict]:
        """
        Resolve a commit identifier to a list of matching commit dicts.

        If a blank identifier is requested, resolve to a list with just the latest commit.

        Tries to find prefix partial matches if an exact match is not found.

        Commit dicts are returned in descending commit time order.

        :raises KeyError: if an exact or partial identifier is not found
        :raises IndexError: if there are no commits
        """
        commits = self.load_commit_list()

        if commit_identifier:
            # try to find exact match before sorting...
            by_identifier = {c["identifier"]: c for c in commits}
            exact_commit = by_identifier.get(commit_identifier)
            if exact_commit:
                return [exact_commit]

        sorted_commits = sorted(
            (c for c in commits if not c.get("adhoc")),
            key=lambda c: str(c["commit_time"]),
            reverse=True,
        )

        if commit_identifier:
            partial_matches = [c for c in sorted_commits if c["identifier"].startswith(commit_identifier)]
            if not partial_matches:
                raise KeyError(commit_identifier)
            return partial_matches

        newest_commit = sorted_commits[0]
        assert newest_commit["identifier"]
        return [newest_commit]

    def load_full_commit(self, identifier: str | None = None) -> dict:
        """
        Load the commit object including config data (as a dict) from the Valohai host for the given commit identifier.

        :param identifier: Identifier; None to use the latest commit on the server.
        """
        for commit in self.load_commit_list():
            if commit.get("adhoc"):
                continue
            if not identifier or commit["identifier"] == identifier:
                data = request(method="get", url=commit["url"], params={"include": "config"}).json()
                assert isinstance(data, dict)
                return data

        raise ValueError(f"No commit found for commit {identifier}")

    def refresh_details(self) -> None:
        """
        Refresh the project details from the API.
        """
        data = request(
            "get",
            f"/api/v0/projects/{self.id}/",
        ).json()
        self.data.update(data)

    def __str__(self) -> str:
        return self.name
