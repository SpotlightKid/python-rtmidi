.PHONY: clean-pyc clean-build clean coverage docs dist lint release release_upload requirements test

BUILDDIR ?= builddir
PREFIX ?= /usr/local
PYTHON ?= python3
SOURCES = src/_rtmidi.pyx src/rtmidi/RtMidi.cpp

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
	@echo "requirements - generate 'requirement-dev.txt' from 'requirements-dev.in'"
	@echo "test - run tests on every supported Python version with tox"

build: $(SOURCES)
	if [[ -d "$(BUILDDIR)" ]]; then \
		meson setup --reconfigure "--prefix=$(PREFIX)" --buildtype=plain $(BUILDDIR); \
	else \
		meson setup "--prefix=$(PREFIX)" --buildtype=plain $(BUILDDIR); \
	fi
	meson compile -C $(BUILDDIR)

check-docs:
	$(PYTHON) -m pydocstyle rtmidi

clean: clean-build clean-docs clean-pyc
	rm -fr htmlcov/

clean-build:
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
	$(PYTHON) -mcoverage run --source rtmidi test
	$(PYTHON) -mcoverage report -m
	$(PYTHON) -mcoverage html
	-xdg-open htmlcov/index.html

dist: clean release
	ls -l dist

docs: build
	cp -f $(BUILDDIR)/rtmidi/_rtmidi.*.so rtmidi/
	cp -f $(BUILDDIR)/rtmidi/version.py rtmidi/
	rm -f docs/rtmidi.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs rtmidi
	cat docs/api.rst.inc >> docs/rtmidi.rst
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	-rm -f rtmidi/*.so rtmidi/version.py
	-xdg-open docs/_build/html/index.html

lint:
	$(PYTHON) -m flake8 rtmidi tests examples

release:
	$(PYTHON) -m build

release_upload: release
	$(PYTHON) -m twine upload --skip-existing dist/*.tar.gz dist/*.whl

requirements-dev.txt: requirements-dev.in
	pip-compile --quiet --resolver=backtracking --no-emit-index-url "$<" > "$@"

requirements: requirements-dev.txt

test:
	pytest -v tests
