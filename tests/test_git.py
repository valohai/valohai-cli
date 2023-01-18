import pytest

from tests.stub_git import StubGit
from valohai_cli.git import (
    describe_current_commit,
    expand_commit_id,
    get_current_commit,
    get_file_at_commit,
)


class TestGit:

    @pytest.fixture(scope='class')
    def my_git(self, stub_git) -> StubGit:
        stub_git.write('README.md', content='This is very important')
        stub_git.commit(message='Initial commit')
        stub_git.write('greeting.txt', content='Hello World!')
        stub_git.commit(message='Add greeting.txt')
        stub_git.write('greeting.txt', content='Hola!')
        stub_git.commit(message='Edit greeting.txt')
        stub_git.write('README.md', content='This is more important')
        stub_git.commit(message='Edit README.md')
        return stub_git

    def test_get_current_commit(self, my_git):
        assert len(get_current_commit(my_git.dir_str)) == 40

    def test_describe_current_commit(self, my_git):
        assert 'heads/' in describe_current_commit(my_git.dir_str)

    def test_get_file_at_commit(self, my_git):
        log = my_git.log()
        content = get_file_at_commit(my_git.dir_str, log[2], 'greeting.txt').decode('utf-8')
        assert content == 'Hello World!'
        content = get_file_at_commit(my_git.dir_str, log[1], 'greeting.txt').decode('utf-8')
        assert content == 'Hola!'

    def test_expand_commit_id(self, my_git):
        latest = my_git.log()[0]
        assert expand_commit_id(my_git.dir_str, 'HEAD') == latest
        assert expand_commit_id(my_git.dir_str, latest[:10]) == latest
