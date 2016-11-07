.PHONY: clean-pyc clean-build docs clean

PYTHON ?= python
SOURCES = src/_rtmidi.cpp src/RtMidi.cpp

help:
	@echo "build - build extension module (and place it in the rtmidi package)"
	@echo "clean-build - remove build artifacts"
	@echo "clean-docs - remove docs output"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "check-docs - check docstrings with pycodestyle"
	@echo "test - run tests with the default Python against working dir"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - build distribution packages"

build: $(SOURCES)
	$(PYTHON) setup.py build_ext --inplace

clean: clean-build clean-docs clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr rtmidi/*.so
	rm -fr src/_rtmidi.cpp

clean-docs:
	rm -fr docs/_build

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name __pycache__ -type d -exec rm -rf {} +

lint:
	flake8 rtmidi tests examples

check-docs:
	pydocstyle rtmidi src

test:
	PYTHONPATH=examples $(PYTHON) setup.py test

test-all:
	tox

coverage:
	coverage run --source rtmidi setup.py test
	coverage report -m
	coverage html
	xdg-open htmlcov/index.html

docs: release
	rm -f docs/rtmidi.rst
	rm -f docs/modules.rst
	$(PYTHON) setup.py build_ext --inplace
	sphinx-apidoc -o docs/ rtmidi
	cat docs/classes.rst >> docs/rtmidi.rst
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	xdg-open docs/_build/html/index.html

release: clean
	$(PYTHON) setup.py release

release_upload: clean
	$(PYTHON) setup.py release_upload

dist: clean release
	ls -l dist
