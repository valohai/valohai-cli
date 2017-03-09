import os

import valohai_yaml
from valohai_yaml import ValidationErrors

from valohai_cli.api import request
from valohai_cli.exceptions import InvalidConfig


class Project:

    def __init__(self, data, directory=None):
        self.data = data
        self.directory = directory

    id = property(lambda p: p.data['id'])
    name = property(lambda p: p.data['name'])

    def get_config(self):
        filename = self.get_config_filename()
        try:
            with open(filename) as infp:
                config = valohai_yaml.parse(infp)
                config.project = self
                return config
        except IOError as ioe:
            raise InvalidConfig('Could not read %s' % filename) from ioe
        except ValidationErrors as ves:
            raise InvalidConfig('{filename} is invalid ({n} errors); see `vh lint`'.format(
                filename=filename,
                n=len(ves.errors),
            ))

    def get_config_filename(self):
        return os.path.join(self.directory, 'valohai.yaml')

    def get_execution_from_counter(self, counter, detail=False):
        results = request(
            'get',
            '/api/v0/executions/',
            params={'project': self.id, 'counter': counter}
        ).json()['results']
        assert len(results) <= 1
        if not results:
            raise ValueError('Execution #{counter} does not exist'.format(counter=counter))
        obj = results[0]
        if detail:
            obj = request('get', obj['url']).json()
        return obj
