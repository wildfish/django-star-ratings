#!/usr/bin/env bash

set -e

SCRIPT_DIR=`dirname "${BASH_SOURCE[0]}"`

if [ "$1" == "-f" ] || [[ "$RUN_WEB_TESTS" != "false"  &&  ! "${TRAVIS_PULL_REQUEST}" != "false" ]]; then
    cd $SCRIPT_DIR/../demo;
    python manage.py test;
fi