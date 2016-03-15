#!/usr/bin/env bash


export DATASERV_MAX_PING="10"
export DATASERV_CLIENT_CONNECTION_RETRY_DELAY="1"
export DATASERV_CACHING_TIME="0"
export PYCOIN_NATIVE="openssl"


# get paths
BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
TMP_SERVER_DIR=/tmp/dataserv_$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c6)


# setup server
git clone https://github.com/Storj/dataserv -b develop $TMP_SERVER_DIR
pip install -r $TMP_SERVER_DIR/requirements.txt
cd $TMP_SERVER_DIR/dataserv
python app.py db upgrade

# start server
python app.py runserver < /dev/null &>/dev/null &
