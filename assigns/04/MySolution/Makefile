NPM ?= npm
PYTHON ?= python3

.PHONY: all install build test run clean

all: build

install:
	$(NPM) ci

build:
	$(NPM) run build

test:
	$(NPM) test

run: build
	$(PYTHON) source/backend.py

clean:
	rm -rf build
