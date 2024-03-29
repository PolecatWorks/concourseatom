

PYTHON := venv/bin/python
PIP := venv/bin/pip
PYTEST := venv/bin/pytest
FLAKE8 := venv/bin/flake8
BLACK  := venv/bin/black
PYLINT := venv/bin/pylint
POETRY := venv/bin/poetry
DETECT_SECRETS := venv/bin/detect-secrets


PYTEST_ARGS=-rP --pdb


.PHONY: docs


info:
	@echo pip = $(PIP)
	@echo python = $(PYTHON)

venv:
	python3 -m venv venv
	$(PIP) install poetry
	$(POETRY) install --with dev
	$(PIP) install -e .[dev]

test:
	$(PYTEST) ${PYTEST_ARGS}
	# -k Resource

coverage: export PYTEST_ARGS=--cov-report xml:cov.xml --cov=concourseatom
coverage: test

docs:
	cd docs && make html

docs-watch:
	cd docs && make autobuild

doctest:
	cd docs && make doctest

flake8:
	$(FLAKE8) .

pylint:
	$(PYLINT) .

format:
	$(BLACK) .

pre-commit:
	pre-commit run --all-files

secrets-baseline:
	$(DETECT_SECRETS) scan > .secrets.baseline

cleanbranches:
	git branch --merged| egrep -v "(^\*|master|main|dev)" | xargs git branch -d

create-patch:
	git diff > concourseatom-$(shell date +"%Y%m%d").patch

publish:
	poetry build
	poetry publish

clean-branches:
	git branch --merged | egrep -v "(^\*|master|main|dev)" | xargs git branch -d
