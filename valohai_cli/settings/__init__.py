import warnings

from valohai_cli.exceptions import APINotFoundError
from valohai_cli.messages import error, info
from valohai_cli.utils import walk_directory_parents

from .paths import get_settings_file_name
from .persistence import FilePersistence


class Settings:
    # Non-persistent settings and their defaults:
    output_format = 'human'
    override_project = None

    def __init__(self, persistence=None):
        """

        :param persistence:
        """
        if not persistence:
            persistence = FilePersistence(get_filename=lambda: get_settings_file_name('config.json'))

        self.persistence = persistence
        self.overrides = {}

    def reset(self):
        self.override_project = None
        self.overrides.clear()

    def _get(self, key, default=None):
        if key in self.overrides:
            return self.overrides[key]
        return self.persistence.get(key, default)

    @property
    def table_format(self):
        warnings.warn('table_format is deprecated; use output_format', category=PendingDeprecationWarning)
        return self.output_format

    @table_format.setter
    def table_format(self, value):
        self.output_format = value

    @property
    def is_human_output(self):
        return (self.output_format == 'human')

    @property
    def user(self):
        """
        The logged in user (dictionary or None).
        :rtype: dict|None
        """
        return self._get('user')

    @property
    def host(self):
        """
        The host we're logged in to (string or None if not logged in).
        :return:
        """
        return self._get('host')

    @property
    def token(self):
        """
        The authentication token we have for the host we're logged in to.
        """
        return self._get('token')

    @property
    def links(self):
        """
        Dictionary of directory <-> project object dicts.
        """
        return self._get('links', {})

    def get_project(self, directory):
        """
        Get the Valohai project object for a directory context.
        The directory tree is walked upwards to find an actual linked directory.

        If a project override is active, it is always returned.

        :param dir: Directory
        :return: Project object, or None.
        :rtype: valohai_cli.models.project.Project|None
        """
        if self.override_project:
            return self.override_project

        links = self.links
        if not links:
            return None
        for directory in walk_directory_parents(directory):
            project_obj = links.get(directory)
            if project_obj:
                from valohai_cli.models.project import Project
                return Project(data=project_obj, directory=directory)

    def set_project_link(self, directory, project):
        if self.override_project:
            raise ValueError('Can not call set_project_link() when an override project is active')

        links = self.links.copy()
        links[directory] = project
        self.persistence.set('links', links)
        assert self.get_project(directory).id == project['id']
        self.persistence.save()

    def set_override_project(self, project_id, directory, mode):
        from valohai_cli.api import request
        from valohai_cli.models.project import Project
        from valohai_cli.models.remote_project import RemoteProject
        assert mode in ('local', 'remote')

        try:
            project_data = request('get', f'/api/v0/projects/{project_id}/').json()
            project_cls = (RemoteProject if mode == 'remote' else Project)
            project = self.override_project = project_cls(data=project_data, directory=directory)
            info('Using project {name} in {mode} (in {directory})'.format(
                name=project.name,
                mode=('local mode' if mode == 'local' else 'remote mode'),
                directory=project.directory,
            ))
            return True
        except APINotFoundError:
            error(f'No project was found with the ID {project_id} (via --project or VALOHAI_PROJECT)')
            return False


settings = Settings()
