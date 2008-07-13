#!/bin/sh

BASE_DIR="/home/www/chrisarndt.de/htdocs/projects/threadpool"
HOST="chris.dilruacs.nl"
USER="chris"

if [ "x$1" != "x-f" ]; then
    RSYNC_OPTS="-n"
fi

rsync $RSYNC_OPTS -av --update --exclude=download --exclude=.svn --delete \
    doc/ "$USER@$HOST:$BASE_DIR"
rsync $RSYNC_OPTS -av --update "--exclude=*.dev*" \
    dist/ "$USER@$HOST:$BASE_DIR/download"
