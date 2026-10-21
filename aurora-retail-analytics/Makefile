VENV := .venv
PY := $(VENV)/bin/python

.PHONY: setup run test

setup:
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) run.py

test:
	$(PY) -m unittest discover -s tests -v
