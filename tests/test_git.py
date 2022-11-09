import pytest

from tests.stub_git import StubGit
from valohai_cli.git import get_current_commit


class TestGit:

    @pytest.fixture(scope='class')
    def my_git(self, stub_git) -> StubGit:
        stub_git.write('test.txt')
        stub_git.commit()
        return stub_git

    def test_get_current_commit(self, my_git):
        assert len(get_current_commit(my_git.dir_str)) == 40
