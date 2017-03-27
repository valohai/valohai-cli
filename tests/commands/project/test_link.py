import pytest

from tests.utils import get_project_data
from valohai_cli.commands.project.link import link
from valohai_cli.commands.project.unlink import unlink
from valohai_cli.ctx import get_project
from valohai_cli.utils import get_random_string
from .utils import get_project_mock


@pytest.mark.parametrize('with_arg', (False, True))
def test_link(runner, logged_in, with_arg):
    project_data = get_project_data(2)
    name = project_data['results'][0]['name']
    with get_project_mock(existing_projects=project_data):
        if with_arg:
            result = runner.invoke(link, [name])  # Parameter on command line
        else:
            result = runner.invoke(link, input='1')  # Interactive choice
        assert 'Linked' in result.output
        assert get_project().name == name


@pytest.mark.parametrize('yes_param', (False, True))
def test_unlink(runner, logged_in_and_linked, yes_param):
    result = runner.invoke(
        unlink,
        ['-y'] if yes_param else [],
        input=('y' if not yes_param else ''),
        catch_exceptions=False,
    )
    assert 'Unlinked' in result.output
    assert not get_project()


def test_unlink_not_linked(runner):
    result = runner.invoke(unlink, catch_exceptions=False)
    assert 'do not seem linked' in result.output


@pytest.mark.parametrize('create', (False, True))
def test_link_no_projs(runner, logged_in, create):
    name = get_random_string()
    with get_project_mock(existing_projects=0, create_project_name=(name if create else None)):
        result = runner.invoke(link, input=('y\n%s\n' % name if create else 'n\n'))
        assert 'Create one instead?' in result.output
        if create:
            assert ('%s created' % name) in result.output


def test_link_no_match(runner, logged_in):
    with get_project_mock(existing_projects=1):
        result = runner.invoke(link, ['fffffffffffffffffffffffffffffff'])
        assert 'No projects match' in result.output


def test_link_projs_create_one_instead(runner, logged_in):
    name = get_random_string()
    with get_project_mock(existing_projects=1, create_project_name=name):
        result = runner.invoke(link, input='n\n%s\n' % name)
        assert 'Name the new project:' in result.output
        assert ('%s created' % name) in result.output
