import os

from tests.commands.project.utils import get_project_mock
from valohai_cli.commands.init import init
from valohai_cli.ctx import get_project
from valohai_cli.utils import get_project_directory, get_random_string


def test_init(runner, logged_in):
    name = get_random_string()
    dir = get_project_directory()
    with open(os.path.join(dir, "my_script.py"), "w") as script_fp:
        script_fp.write("# Hello")

    with get_project_mock(create_project_name=name):
        result = runner.invoke(
            init,
            input="\n".join([
                "y",  # correct directory
                "echo hello",  # command
                "y",  # yes, that's right
                "1",  # image number 1
                "n",  # no, actually
                "",  # erm what
                "docker",  # image called docker, yes
                "y",  # okay, that's better
                "y",  # confirm write
                "c",  # create new
                name,  # that's a nice name
            ]),
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "my_script.py" in result.output
        assert "Happy (machine) learning!" in result.output

        assert os.path.exists(os.path.join(dir, "valohai.yaml"))
        assert get_project(dir)


def test_init_wont_relink(runner, logged_in_and_linked):
    result = runner.invoke(init)
    assert result.exit_code == 1
