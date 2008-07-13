#!/bin/sh

BASE_DIR="/htdocs/en/software/python/"
HOST="chrisarndt.de"
USER="chrisarnde79"
echo -n "Password: "
read PASSWD

ncftpput -R -u "${USER}" -p "${PASSWD}" "${HOST}" "${BASE_DIR}" \
  threadpool.html threadpool.py.html rest.css tp_api

ncftpput -u "${USER}" -p "${PASSWD}" "${HOST}" "${BASE_DIR}/download/" \
  threadpool.py
