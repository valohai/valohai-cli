import os

import click.exceptions
import pytest
import requests_mock

from tests.fixture_data import PROJECT_DATA
from valohai_cli.models.project import Project
from valohai_cli.utils.commits import resolve_commit


class TestResolveCommit:

    commit_api_url = 'https://app.valohai.com/api/v0/commits/'

    @pytest.fixture
    def project(self):
        return Project(data=PROJECT_DATA, directory=os.getcwd())

    @pytest.fixture
    def commits(self):
        return [
            {
                'commit_time': '2022-11-04T12:32:02Z',  # the oldest
                'identifier': 'a9f10d48ed9ece3997b40d2432c64eb08bd11e45',
            },
            {
                'commit_time': '2022-11-04T13:33:03Z',  # has ambiguous extension
                'identifier': 'b5b50f5d183ebc645460dba1329ee48798f31482-alpha',
            },
            {
                'commit_time': '2022-11-04T14:34:04Z',  # has ambiguous extension
                'identifier': 'b5b50f5d183ebc645460dba1329ee48798f31482-beta',
            },
            {
                'commit_time': '2022-11-04T15:35:05Z',  # has extension
                'identifier': '8e8351d22cc14e1eeda8c9a5e81320e19eeed3e4-gamma',
            },
            {
                'commit_time': '2022-11-04T16:36:06Z',  # the latest
                'identifier': 'c243d40ff7feb63aa7e15e8eda1d8859010ebc53',
            }
        ]

    @pytest.mark.parametrize('lookup, expected', [
        # adhoc commit resolves to itself
        ['~d1df3bdb3614731c4ba795fa3c322617a3c996d9', '~d1df3bdb3614731c4ba795fa3c322617a3c996d9'],
        # exact match to extensionless commit identifier
        ['c243d40ff7feb63aa7e15e8eda1d8859010ebc53', 'c243d40ff7feb63aa7e15e8eda1d8859010ebc53'],
        # partial match to extensionless commit identifier
        ['c243d40', 'c243d40ff7feb63aa7e15e8eda1d8859010ebc53'],
        # exact match to commit identifier with an extension
        ['b5b50f5d183ebc645460dba1329ee48798f31482-alpha', 'b5b50f5d183ebc645460dba1329ee48798f31482-alpha'],
    ])
    def test_works(self, capsys, logged_in, project, commits, lookup, expected):
        with requests_mock.mock() as m:
            m.get(self.commit_api_url, json={'results': commits})
            assert resolve_commit(lookup, project=project) == expected
        out, err = capsys.readouterr()
        assert not out
        assert not err

    def test_work_but_warns_if_empty_lookup(self, capsys, logged_in, project, commits):
        with requests_mock.mock() as m:
            m.get(self.commit_api_url, json={'results': commits})
            resolved = resolve_commit('', project=project)
        assert resolved == 'c243d40ff7feb63aa7e15e8eda1d8859010ebc53'
        _out, err = capsys.readouterr()
        assert 'Resolved to commit' in err
        assert 'ambiguous' not in err

    def test_work_but_warns_if_ambiguous(self, capsys, logged_in, project, commits):
        with requests_mock.mock() as m:
            m.get(self.commit_api_url, json={'results': commits})
            # partial match to the latest matching commit identifier with an extension
            resolved = resolve_commit('b5b50f5d183ebc645460dba1329ee48798f31482', project=project)
        assert resolved == 'b5b50f5d183ebc645460dba1329ee48798f31482-beta'
        _out, err = capsys.readouterr()
        assert 'which is ambiguous with' in err

    @pytest.mark.parametrize('confirm', [True, False])
    def test_asks_to_fetch_latest_if_not_found(self, logged_in, project, commits, monkeypatch, confirm):
        new_commit = '94c9d70834f53ce765f3b86bac50f015278d8bd4'
        with requests_mock.mock() as m:
            m.get(self.commit_api_url, json={'results': commits})

            # When the commit is not found, it should ask to fetch latest commits
            monkeypatch.setattr(click, 'confirm', lambda *args, **kwargs: confirm)

            if confirm:
                # When the latest commit is fetched, it should return the new commit
                monkeypatch.setattr('valohai_cli.utils.commits.fetch_latest_commits', lambda unknown_commit: [{'identifier': new_commit}])
                assert resolve_commit(new_commit, project) == new_commit
            else:
                with pytest.raises(click.exceptions.Abort):
                    resolve_commit(new_commit, project)

    def test_fails_if_no_commits(self, logged_in, project, monkeypatch):
        with requests_mock.mock() as m:
            m.get(self.commit_api_url, json={'results': []})
            monkeypatch.setattr(click, 'confirm', lambda *args, **kwargs: True)
            monkeypatch.setattr('valohai_cli.utils.commits.fetch_latest_commits',
                                lambda unknown_commit: [])
            with pytest.raises(click.exceptions.Abort):
                resolve_commit('c243d40ff7feb63aa7e15e8eda1d8859010ebc53', project)
