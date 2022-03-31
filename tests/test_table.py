from valohai_cli.table import print_table


def test_print_csv(capsys):
    print_table([{"a": 1, "b": 2}, {"a": 3, "b": 4}], format="csv")
    assert capsys.readouterr().out == "a,b\n1,2\n3,4\n"
