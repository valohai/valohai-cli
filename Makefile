UV := $(shell command -v uv)
ifdef UV
    PIP_INSTALL = uv pip install
else
    PIP_INSTALL = pip install
endif

.PHONY: default
default:
	@echo "check README for usage"

.PHONY: dev
dev:
ifndef UV
	pip install -U pip
endif
	$(PIP_INSTALL) -r requirements-test.txt
	$(PIP_INSTALL) pre-commit
	$(PIP_INSTALL) -e .
	pre-commit install

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: test
test:
	py.test -vvv --cov .
