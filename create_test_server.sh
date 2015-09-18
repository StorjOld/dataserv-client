#!/usr/bin/env bash

BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
TMP_SERVER_DIR=/tmp/dataserv_$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c6)
PY=$BASE_DIR/env/bin/python
PIP=$BASE_DIR/env/bin/pip

# setup server
export DATASERV_MAX_PING="10"
git clone https://github.com/Storj/dataserv $TMP_SERVER_DIR
$PIP install -r $TMP_SERVER_DIR/requirements.txt
cd $TMP_SERVER_DIR/dataserv
$PY app.py db upgrade
$PY app.py runserver
