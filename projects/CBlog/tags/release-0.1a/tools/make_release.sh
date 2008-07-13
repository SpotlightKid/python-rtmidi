#!/bin/sh

PYTHONPATH='.' cheetah fill --iext .in --oext .rst README.in
RST2HTML=$(which rst2html 2>/dev/null)
if [ -z "$RST2HTML" ]; then
    RST2HTML=$(which rst2html.py 2>/dev/null)
fi
"$RST2HTML" --date --time README.rst >README.html
python setup.py sdist --formats=zip,bztar
python setup.py bdist_egg
