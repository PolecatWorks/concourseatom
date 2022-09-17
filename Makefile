

PYTHON := venv/bin/python
PIP := venv/bin/pip
PYTEST := venv/bin/pytest

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
