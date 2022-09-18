

PYTHON := venv/bin/python
PIP := venv/bin/pip
PYTEST := venv/bin/pytest
FLAKE8 := venv/bin/flake8
BLACK  := venv/bin/black
PYLINT := venv/bin/pylint

.PHONY: docs


info:
	@echo pip = $(PIP)
	@echo python = $(PYTHON)

venv:
	python3 -m venv venv
	$(PIP) install -r requirements.txt

test:
	$(PYTEST) -rP --pdb -k FullThing_merge
	# -k Resource

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
