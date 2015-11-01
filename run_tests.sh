#!/usr/bin/env bash


export DATASERV_MAX_PING="10"
export DATASERV_CLIENT_CONNECTION_RETRY_DELAY="1"
export DATASERV_CACHING_TIME="0"


# get paths
BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
TMP_SERVER_DIR=/tmp/dataserv_$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c6)
PY=$BASE_DIR/env/bin/python
PIP=$BASE_DIR/env/bin/pip


# setup server
git clone https://github.com/Storj/dataserv -b develop $TMP_SERVER_DIR
$PIP install -r $TMP_SERVER_DIR/requirements.txt
cd $TMP_SERVER_DIR/dataserv
$PY app.py db upgrade

# run server
screen -S testserver -d -m $PY app.py runserver


# run tests
cd $BASE_DIR
$PY setup.py test


# clean up
screen -S testserver -X kill
rm -rf $TMP_SERVER_DIR
