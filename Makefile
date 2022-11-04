.PHONY: default
default:
	@echo "check README for usage"

.PHONY: mypy
mypy:
	mypy valohai_cli --show-error-code --incremental --strict --disable-error-code=type-arg

.PHONY: lint
lint:
	flake8

.PHONY: test
test:
	py.test -vvv --cov .
