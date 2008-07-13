#!/bin/sh

BASE_DIR="/htdocs/projects/"
HOST="chrisarndt.de"
USER="chrisarnde79"

lftp  -u $USER "ftp://${HOST}" -e 'cd '${BASE_DIR}'; mirror -Rnv --exclude '.svn' doc fancyflash; quit'
