from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

from valohai_cli.exceptions import APINotFoundError
from valohai_cli.messages import error, info
from valohai_cli.utils import walk_directory_parents

from .paths import get_settings_file_name
from .persistence import FilePersistence, Persistence

if TYPE_CHECKING:
    from ..models.project import Project
    from ..models.remote_project import RemoteProject


class Settings:
    # Non-persistent settings and their defaults:
    output_format = "human"
    override_project = None
    api_user_agent_prefix = None

    def __init__(self, persistence: Persistence | None = None) -> None:
        if not persistence:
            persistence = FilePersistence(get_filename=lambda: get_settings_file_name("config.json"))

        self.persistence: Persistence = persistence
        self.overrides: dict[str, Any] = {}

    def reset(self) -> None:
        self.override_project = None
        self.overrides.clear()

    def _get(self, key: str, default: Any = None) -> Any | None:
        if key in self.overrides:
            return self.overrides[key]
        return self.persistence.get(key, default)

    @property
    def table_format(self) -> str:
        warnings.warn(
            "table_format is deprecated; use output_format",
            category=PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.output_format

    @table_format.setter
    def table_format(self, value: str) -> None:
        self.output_format = value

    @property
    def is_human_output(self) -> bool:
        return self.output_format == "human"

    @property
    def user(self) -> dict | None:
        """
        The logged in user (dictionary or None).
        """
        return self._get("user")

    @property
    def host(self) -> str | None:
        """
        The host we're logged in to (string or None if not logged in).
        """
        return self._get("host")

    @property
    def verify_ssl(self) -> bool | str:
        """
        Whether to verify SSL connections to the Valohai API, or a path to a CA bundle.
        """
        value = self._get("verify_ssl", default=True)
        if value is True or value is False:
            return value
        return str(value)

    @property
    def token(self) -> str | None:
        """
        The authentication token we have for the host we're logged in to.
        """
        return self._get("token")

    @property
    def links(self) -> dict:
        """
        Dictionary of directory <-> project object dicts.
        """
        links = self._get("links")
        if isinstance(links, dict):
            return links
        return {}

    def get_project(self, directory: str) -> RemoteProject | Project | None:
        """
        Get the Valohai project object for a directory context.
        The directory tree is walked upwards to find an actual linked directory.

        If a project override is active, it is always returned.

        :param dir: Directory
        :return: Project object, or None.
        """
        if self.override_project:
            return self.override_project

        links = self.links
        if not links:
            return None
        for directory in walk_directory_parents(directory):  # noqa: B020
            project_obj = links.get(directory)
            if project_obj:
                from valohai_cli.models.project import Project

                return Project(data=project_obj, directory=directory)
        return None  # No project.

    def set_project_link(self, directory: str, project: dict) -> None:
        if self.override_project:
            raise ValueError("Can not call set_project_link() when an override project is active")

        links = self.links.copy()
        links[directory] = project
        self.persistence.set("links", links)
        project_for_dir = self.get_project(directory)
        assert project_for_dir and project_for_dir.id == project["id"]
        self.persistence.save()

    def set_override_project(self, project_id: str, directory: str, mode: str) -> bool:
        from valohai_cli.api import request
        from valohai_cli.models.project import Project
        from valohai_cli.models.remote_project import RemoteProject

        assert mode in ("local", "remote")

        try:
            project_data = request("get", f"/api/v0/projects/{project_id}/").json()
            project_cls = RemoteProject if mode == "remote" else Project
            project = self.override_project = project_cls(data=project_data, directory=directory)
            mode_fmt = "local mode" if mode == "local" else "remote mode"
            info(f"Using project {project.name} in {mode_fmt} (in {project.directory})")
            return True
        except APINotFoundError:
            error(f"No project was found with the ID {project_id} (via --project or VALOHAI_PROJECT)")
            return False


settings = Settings()
