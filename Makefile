.PHONY: default
default:
	echo "Try another target"

.PHONY: mypy
mypy:
	mypy valohai_cli --show-error-code --incremental --strict --disable-error-code=type-arg

.PHONY: lint
lint:
	flake8

.PHONY: test
test:
	py.test -vvv --cov .
