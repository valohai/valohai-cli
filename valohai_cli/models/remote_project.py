from valohai_cli.models.project import Project


class RemoteProject(Project):
    is_remote = True

    def get_config(self, commit_identifier=None):
        if not commit_identifier:
            raise ValueError('RemoteProjects require an explicit commit identifier')
        commit = self.load_full_commit(commit_identifier)
        if not commit:
            raise ValueError('No configuration found for commit %s' % commit_identifier)
        return self._parse_config(commit['config'], filename='<remote config>')

    def get_config_filename(self):  # pragma: no cover
        raise NotImplementedError('RemoteProject.get_config_filename() should never get called')
