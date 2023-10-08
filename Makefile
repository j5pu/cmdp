.PHONY: build docs tests venv
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PACKAGE := $(shell basename $(ROOT_DIR))
PYTHONPATH := $(ROOT_DIR)/src
export PYTHONPATH

brew:
	@python3 -m $(PACKAGE) $@ --command gh

browser:
	@python3 -m $(PACKAGE) $@

build:  # Build a project `venv`, `completions`, `docs` and `clean`.
	@python3 -m $(PACKAGE) $@

clean:
	@python3 -m $(PACKAGE) $@

commit: tests
	@python3 -m $(PACKAGE) $@

completions:
	@python3 -m $(PACKAGE) $@

coverage:
	@python3 -m $(PACKAGE) $@

docs:
	@python3 -m $(PACKAGE) $@

latest:
	@python3 -m $(PACKAGE) $@

next:
	@python3 -m $(PACKAGE) $@

publish:  # runs `tests`, `commit`, `tag`, `push`, `twine` and `clean`
	@python3 -m $(PACKAGE) $@

pyenv:
	@pyenv install 3.11
	@pyenv install 3.12-dev

pytest:
	@python3 -m $(PACKAGE) $@

requirements:
	@python3 -m $(PACKAGE) $@ --install

ruff:
	@python3 -m $(PACKAGE) $@

secrets:
	@python3 -m $(PACKAGE) $@

tests:  # runs `build`, `ruff`, `pytest` and `tox`
	@python3 -m $(PACKAGE) $@

tox:
	@python3 -m $(PACKAGE) $@

twine:
	@python3 -m $(PACKAGE) $@

venv:  # runs `write` and `requirements`
	@python3 -m $(PACKAGE) $@

.DEFAULT_GOAL := publish
