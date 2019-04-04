import os

import six
import valohai_yaml
from click import BadParameter

from valohai_cli.api import request
from valohai_cli.exceptions import InvalidConfig, NoExecution, APIError
from valohai_cli.git import get_file_at_commit


class Project:
    is_remote = False

    def __init__(self, data, directory=None):
        self.data = data
        self.directory = directory
        self._commit_list = None

    id = property(lambda p: p.data['id'])
    name = property(lambda p: p.data['name'])

    def get_config(self, commit_identifier=None):
        """
        Get the `valohai_yaml.Config` object from the current working directory,
        or a given commit.

        :param commit_identifier: Hexadecimal commit identifier; optional.
        :type commit_identifier: str|None
        :return: valohai_yaml.Config
        :rtype: valohai_yaml.Config
        """
        if not commit_identifier:  # Current working directory
            filename = self.get_config_filename()
            with open(filename, 'r') as infp:
                return self._parse_config(infp, filename)
        else:  # Arbitrary commit
            filename = '{}:valohai.yaml'.format(commit_identifier)
            config_bytes = get_file_at_commit(self.directory, commit_identifier, 'valohai.yaml')
            config_sio = six.StringIO(config_bytes.decode('utf-8'))
            return self._parse_config(config_sio, filename)

    def _parse_config(self, config_fp, filename='<config file>'):
        try:
            config = valohai_yaml.parse(config_fp)
            config.project = self
            return config
        except IOError as ioe:
            six.raise_from(InvalidConfig('Could not read %s' % filename), ioe)
        except valohai_yaml.ValidationErrors as ves:
            raise InvalidConfig('{filename} is invalid ({n} errors); see `vh lint`'.format(
                filename=filename,
                n=len(ves.errors),
            ))

    def get_config_filename(self):
        return os.path.join(self.directory, 'valohai.yaml')

    def get_execution_from_counter(self, counter, params=None):
        if isinstance(counter, str):
            counter = counter.lstrip('#')
            if not (counter.isdigit() or counter == 'latest'):
                raise BadParameter(
                    '{counter} is not a valid counter value; it must be an integer or "latest"'.format(counter=counter),
                )
        try:
            return request(
                method='get',
                url='/api/v0/executions/{project_id}:{counter}/'.format(project_id=self.id, counter=counter),
                params=(params or {}),
            ).json()
        except APIError as ae:
            if ae.response.status_code == 404:
                raise NoExecution('Execution #{counter} does not exist'.format(counter=counter))
            raise

    def load_commit_list(self):
        """
        Get a list of non-adhoc commits, newest first.
        """
        if self._commit_list is None:
            commits = list(request(
                method='get',
                url='/api/v0/commits/',
                params={
                    'project': self.id,
                    'adhoc': 'false',
                    'limit': 9000,
                },
            ).json()['results'])
            commits.sort(key=lambda c: c['commit_time'], reverse=True)
            self._commit_list = commits
        return self._commit_list

    def resolve_commit(self, commit_identifier=None):
        """
        Resolve a commit identifier to a commit dict.
        :param commit_identifier:
        :return: dict
        :raises KeyError: if an explicitly named identifier is not found
        :raises IndexError: if there are no commits
        """
        commits = self.load_commit_list()
        if commit_identifier:
            by_identifier = {c['identifier']: c for c in commits}
            return by_identifier[commit_identifier]
        newest_commit = sorted(
            [c for c in commits if not c.get('adhoc')],
            key=lambda c: c['commit_time'],
            reverse=True,
        )[0]
        assert newest_commit['identifier']
        return newest_commit

    def load_full_commit(self, identifier=None):
        """
        Load the commit object including config data (as a dict) from the Valohai host for the given commit identifier.

        :param identifier: Identifier; None to use the latest commit on the server.
        """
        for commit in self.load_commit_list():
            if commit.get('adhoc'):
                continue
            if not identifier or commit['identifier'] == identifier:
                return request(method='get', url=commit['url'], params={'include': 'config'}).json()

        raise ValueError('No commit found for commit %s' % identifier)

    def __str__(self):
        return self.name
