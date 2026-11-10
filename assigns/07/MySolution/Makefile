.PHONY: install test test-http test-all serve

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -r requirements.txt

# Run the in-process suites under MySolution/tests.
test:
	cd .. && $(PYTHON) -m unittest discover -s MySolution/tests -v

# Start a local server for the supplied black-box HTTP contract suite.
test-http:
	server_pid=; $(PYTHON) server.py & server_pid=$$!; trap 'kill "$$server_pid" 2>/dev/null || true' EXIT INT TERM; sleep 1; cd .. && $(PYTHON) -m unittest discover -s TEST -v

# Run both the focused and supplied HTTP-level suites.
test-all: test test-http

# Start the service at http://127.0.0.1:8000/rpc.
serve:
	python3 server.py
