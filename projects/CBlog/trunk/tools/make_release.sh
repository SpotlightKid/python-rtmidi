#!/bin/sh

RST2HTML_OPTS='--stylesheet-path=rest.css --link-stylesheet'
PYTHONPATH='.' cheetah fill --iext .in --oext .rst --odir doc README.in
test $? -eq 0 || exit 1
RST2HTML=$(which rst2html 2>/dev/null)
if [ -z "$RST2HTML" ]; then
    RST2HTML=$(which rst2html.py 2>/dev/null)
fi
( cd doc;  "$RST2HTML" $RST2HTML_OPTS --date --time README.rst >README.html; )
python setup.py sdist --formats=zip,bztar
python setup.py bdist_egg
