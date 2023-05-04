# PN - Project Name
PN := airflow_declarative
# PV - Project Version
PV := `poetry version -s`

PYTHON := python3
SHELL  := /bin/sh

LINT_TARGET := src/ tests/

SPHINXOPTS  ?= -n -W

.PHONY: all
all: help


.PHONY: check
# target: check - Run all checks: linters and tests (with coverage)
check: lint test check-docs


.PHONY: check-docs
# target: check-docs - Run Sphinx but don't actually generate the docs
check-docs:
	@# Doesn't generate any output but prints out errors and warnings.
	@. ./airflow_env.sh && sphinx-build -M dummy src/docs build/docs $(SPHINXOPTS)


.PHONY: clean
# target: clean - Remove intermediate and generated files
clean:
	@${PYTHON} setup.py clean
	@find . -type f -name '*.py[co]' -delete
	@find . -type d -name '__pycache__' -delete
	@rm -rf {build,htmlcov,cover,coverage,dist,.coverage,.hypothesis}
	@rm -rf src/*.egg-info
	@rm -f VERSION


.PHONY: develop
# target: develop - Install package in editable mode with `develop` extras
develop:
	@poetry install --sync


.PHONY: dist
# target: dist - Build all artifacts
dist:
	@poetry build


.PHONY: docs
# target: docs - Build Sphinx docs
docs:
	@. ./airflow_env.sh && sphinx-build -M html src/docs build/docs $(SPHINXOPTS)

.PHONY: format
# target: format - Format the code according to the coding styles
format: format-black format-isort


.PHONY: format-black
format-black:
	@black ${LINT_TARGET}


.PHONY: format-isort
format-isort:
	@isort ${LINT_TARGET}


.PHONY: help
# target: help - Print this help
help:
	@egrep "^# target: " Makefile \
		| sed -e 's/^# target: //g' \
		| sort -h \
		| awk '{printf("    %-16s", $$1); $$1=$$2=""; print "-" $$0}'


.PHONY: install
# target: install - Install the project
install:
	@pip install .


.PHONY: lint
# target: lint - Check source code with linters
lint: lint-isort lint-black lint-flake8 lint-pylint


.PHONY: lint-black
lint-black:
	@${PYTHON} -m black --check --diff ${LINT_TARGET}


.PHONY: lint-flake8
lint-flake8:
	@${PYTHON} -m flake8 --statistics ${LINT_TARGET}


.PHONY: lint-isort
lint-isort:
	@${PYTHON} -m isort -c ${LINT_TARGET}


.PHONY: lint-pylint
lint-pylint:
	@${PYTHON} -m pylint --rcfile=.pylintrc --errors-only ${LINT_TARGET}


.PHONY: report-coverage
# target: report-coverage - Print coverage report
report-coverage:
	@${PYTHON} -m coverage report


.PHONY: report-pylint
# target: report-pylint - Generate pylint report
report-pylint:
	@${PYTHON} -m pylint ${LINT_TARGET}


.PHONY: test
# target: test - Run tests with coverage
test:
	@. ./airflow_env.sh && ${PYTHON} -m coverage run -m pytest
	@${PYTHON} -m coverage report


.PHONY: version
# target: version - Generate and print project version in PEP-440 format
version: VERSION
	@cat VERSION
VERSION:
	@echo ${PV} > $@
