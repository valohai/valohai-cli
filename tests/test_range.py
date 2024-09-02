from valohai_cli.range import IntegerRange


def test_range():
    assert IntegerRange.parse([1, "2", "3", "4-10", "!8"]).as_set() == {1, 2, 3, 4, 5, 6, 7, 9, 10}
