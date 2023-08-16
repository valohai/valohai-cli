.PHONY: default
default:
	@echo "check README for usage"

.PHONY: dev
dev:
	pip install -U pip
	pip install -r requirements-test.txt
	pip install pre-commit
	pip install -e .
	pre-commit install

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: test
test:
	py.test -vvv --cov .
