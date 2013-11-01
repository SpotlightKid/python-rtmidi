#!/bin/bash

SRCDIR="$HOME/work/python-rtmidi/"
DSTDIR="work/rtmidi/src/python-rtmidi"
DSTHOST="192.168.100.1"

rsync -av --update --checksum \
    --exclude .svn \
    --exclude sysex \
    --exclude dist \
    --exclude build \
    --exclude __pycache__ \
    "$SRCDIR" "$DSTHOST:$DSTDIR"
