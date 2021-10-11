default:
	echo "Try another target"

mypy:
	mypy valohai_cli --show-error-code --incremental --strict --disable-error-code=type-arg

lint:
	flake8

test:
	py.test -vvv --cov .
