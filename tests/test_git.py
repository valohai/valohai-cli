from __future__ import unicode_literals
from subprocess import check_call

from valohai_cli.git import get_current_commit


def test_get_current_commit(tmpdir):
    dir = str(tmpdir)
    check_call('git init', cwd=dir, shell=True)
    check_call('git config user.name Robot', cwd=dir, shell=True)
    check_call('git config user.email robot@example.com', cwd=dir, shell=True)
    tmpdir.join('test').write_text('test', 'utf8')
    check_call('git add .', cwd=dir, shell=True)
    check_call('git commit -mtest', cwd=dir, shell=True)
    assert len(get_current_commit(dir)) == 40
