

PYTHON := venv/bin/python
PIP := venv/bin/pip


info:
	@echo pip = $(PIP)
	@echo python = $(PYTHON)

venv:
	python3 -m venv venv
	$(PIP) install -r requirements.txt
