#!/bin/bash

# generates documentation files and packages distribution archive

# before you run this, check that the version numbers in README.txt, setup.py
# and threadpool.py are correct.

VENV="venv"
RST2HTML_OPTS='--stylesheet-path=rest.css --link-stylesheet --input-encoding=UTF-8 --output-encoding=UTF-8 --language=en --no-xml-declaration --date --time'

if [ -d "$VENV" ]; then
    source "$VENV/bin/activate"
fi


# Create HTML file with syntax highlighted source
pygmentize  -P full -P cssfile=hilight.css -P title=threadpool.py \
    -o doc/threadpool.py.html src/threadpool.py
# Create API documentation
epydoc -v -n Threadpool -o doc/api \
  --url "http://chrisarndt.de/projects/threadpool/" \
  --no-private --docformat restructuredtext \
  src/threadpool.py
# Create HTMl version of README
rst2html.py $RST2HTML_OPTS README.txt >doc/index.html

if [ "x$1" = "xregister" ]; then
    shift
    python setup.py release register
fi
if [ "x$1" = "xupload" ]; then
    python setup.py release sdist --formats=bztar,zip bdist_egg upload
else
    python setup.py sdist --formats=bztar,zip bdist_egg
fi
