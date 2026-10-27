PYTHON ?= python3
ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
all:
	PYTHONPATH=$(ROOT) $(PYTHON) -m unittest discover -s $(ROOT)tests -p 'test_*.py'
	PYTHONPATH=$(ROOT) $(PYTHON) $(ROOT)demo.py
clean:
	find $(ROOT) -type d -name __pycache__ -prune -exec rm -rf {} +
