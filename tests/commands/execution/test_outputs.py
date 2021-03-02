import os

import pytest

from tests.commands.execution.utils import get_execution_data_mock
from tests.fixture_data import EXECUTION_DATA, OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA
from valohai_cli.commands.execution.outputs import outputs


@pytest.mark.parametrize('download', (False, True))
def test_execution_outputs(runner, logged_in_and_linked, tmpdir, download):
    tmpdir = str(tmpdir)

    with get_execution_data_mock() as m:
        m.get(OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA['url'], content=b'0' * 100)
        params = [str(EXECUTION_DATA['counter'])]
        if download:
            params.append(f'--download={tmpdir}')
        output = runner.invoke(outputs, params, catch_exceptions=False).output
        assert all(o['name'] in output for o in EXECUTION_DATA['outputs'])
        if download:
            # See that things were downloaded
            for output in EXECUTION_DATA['outputs']:
                assert os.path.exists(os.path.join(tmpdir, output['name']))
