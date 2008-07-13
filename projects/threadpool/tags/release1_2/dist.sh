#!/bin/sh

COLORIZE="/mnt/win2k/WINNT/scripts/colorize.py"

python "$COLORIZE" threadpool.py >threadpool.py.html
epydoc -n Threadpool  -o tp_api \
  --url "http://chrisarndt.de/en/software/python/threadpool.html" \
  --no-private --docformat restructuredtext \
  threadpool.py
rest2html --stylesheet=rest.css README.txt >threadpool.html

