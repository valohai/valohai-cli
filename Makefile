.PHONY: default
default:
	@echo "check README for usage"

.PHONY: dev
dev:
	pip install -U pip
	pip install -r requirements-test.txt
	pip install -e .

.PHONY: test
test:
	py.test -vvv --cov .
