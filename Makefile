.PHONY: clean-pyc clean-build docs clean

PYTHON ?= python
SOURCES = src/_rtmidi.cpp src/RtMidi.cpp

help:
	@echo "build - build extension module (and place it in the rtmidi package)"
	@echo "check-docs - check docstrings with pycodestyle"
	@echo "clean-build - remove build artifacts"
	@echo "clean-docs - remove docs output"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "dist - build distribution packages"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "lint - check style with flake8"
	@echo "release - package a release"
	@echo "release_upload - package a release and upload it to PyPI"
	@echo "test - run tests on every supported Python version with tox"

build: $(SOURCES)
	$(PYTHON) setup.py build_ext --inplace

check-docs:
	pydocstyle rtmidi src

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

coverage:
	coverage run --source rtmidi setup.py test
	coverage report -m
	coverage html
	xdg-open htmlcov/index.html

dist: clean release
	ls -l dist

docs: release
	rm -f docs/rtmidi.rst
	rm -f docs/modules.rst
	$(PYTHON) setup.py build_ext --inplace
	sphinx-apidoc -o docs/ rtmidi rtmidi/release.py
	cat docs/api.rst.inc >> docs/rtmidi.rst
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	xdg-open docs/_build/html/index.html

lint:
	flake8 rtmidi tests examples

release: clean
	$(PYTHON) setup.py release

release_upload: release
	twine upload --skip-existing dist/*.tar.gz

test:
	PYTHONPATH=examples $(PYTHON) setup.py test
