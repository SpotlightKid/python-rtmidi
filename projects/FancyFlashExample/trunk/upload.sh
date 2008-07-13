#!/bin/sh

BASE_DIR="/htdocs/projects/"
HOST="chrisarndt.de"
USER="chrisarnde79"

lftp -u $USER "ftp://${HOST}" \
  -e 'cd '${BASE_DIR}'; mirror -Rnv --exclude '.svn' dist fancyflashexample; cd fancyflashexample; put README.html -o index.html; put rest.css; quit'
