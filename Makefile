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
	$(PIP_INSTALL) prek -e .[test]
	prek install

.PHONY: lint
lint:
	prek run --all-files

.PHONY: test
test:
	py.test -vvv --cov .
