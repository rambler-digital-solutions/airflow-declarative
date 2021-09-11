# PN - Project Name
PN := airflow_declarative
# PN - Project Version
PV := `python setup.py -q --version`

PYTHON_VENV := python3
PYTHON := python
SHELL  := /bin/sh

LINT_TARGET := setup.py src/ tests/

SPHINXOPTS  ?= -n -W

.PHONY: all
all: help


.PHONY: check
# target: check - Run all checks: linters and tests (with coverage)
check: lint test check-docs
	@${PYTHON} setup.py check


.PHONY: check-docs
# target: check-docs - Run Sphinx but don't actually generate the docs
check-docs:
	@# Doesn't generate any output but prints out errors and warnings.
	@sphinx-build -M dummy src/docs build/docs $(SPHINXOPTS)


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
	@${PYTHON} -m pip install --upgrade pip setuptools wheel
	@${PYTHON} -m pip install --upgrade 'apache-airflow<2.2,>=2.1'
	@${PYTHON} -m pip install -e '.[develop]'


.PHONY: dist
# target: dist - Build all artifacts
dist: dist-sdist dist-wheel


.PHONY: dist-sdist
# target: dist-sdist - Build sdist artifact
dist-sdist:
	@${PYTHON} setup.py sdist


.PHONY: dist-wheel
# target: dist-wheel - Build wheel artifact
dist-wheel:
	@${PYTHON} setup.py bdist_wheel

.PHONY: docs
# target: docs - Build Sphinx docs
docs:
	@sphinx-build -M html src/docs build/docs $(SPHINXOPTS)

.PHONY: format
# target: format - Format the code according to the coding styles
format: format-black format-isort


.PHONY: format-black
format-black:
	@black ${LINT_TARGET}


.PHONY: format-isort
format-isort:
	@isort -rc ${LINT_TARGET}


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
	@${PYTHON} -m isort.main -df -c -rc ${LINT_TARGET}


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
	@${PYTHON} -m coverage run -m py.test
	@${PYTHON} -m coverage report


# `venv` target is intentionally not PHONY.
# target: venv - Creates virtual environment
venv:
	@${PYTHON_VENV} -m venv venv


.PHONY: version
# target: version - Generate and print project version in PEP-440 format
version: VERSION
	@cat VERSION
VERSION:
	@echo ${PV} > $@
