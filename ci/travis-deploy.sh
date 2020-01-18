#!/bin/bash
#
# travis-deploy.sh - Upload Python wheels and source distribution
#                    built by Travis CI to PyPI

set -ev

if [[ $TRAVIS_OS_NAME = 'osx' ]]; then
    ${PYTHON:-python} -m twine upload --skip-existing dist/*.whl
elif [[ $TRAVIS_OS_NAME = 'linux' && $TRAVIS_PYTHON_VERSION = '3.8' ]]; then
    ${PYTHON:-python} -m twine upload --skip-existing dist/*.tar.gz
fi
