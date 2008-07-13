#!/bin/sh

BASE_DIR="/home/www/chrisarndt.de/htdocs/projects/"
HOST="chrisarndt.de"
USER="chris"

ssh "${USER}@${HOST}" mkdir -p "${BASE_DIR}/eggbasket"
rsync -v -r --update doc/ "${USER}@${HOST}:${BASE_DIR}/eggbasket"
