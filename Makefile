.PHONY: default
default:
	@echo "check README for usage"

.PHONY: dev
dev:
	pip install -U pip
	pip install -r requirements-typecheck.txt
	pip install -r requirements-lint.txt
	pip install -r requirements-test.txt
	pip install -e .

.PHONY: mypy
mypy:
	mypy valohai_cli --show-error-code --incremental --strict --disable-error-code=type-arg

.PHONY: lint
lint:
	flake8

.PHONY: test
test:
	py.test -vvv --cov .
