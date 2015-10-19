#!/usr/bin/env bash

SCRIPT_DIR=`dirname "${BASH_SOURCE[0]}"`

if [ -n "$TRAVIS_PULL_REQUEST" ] || [ "$1" == "-f" ]; then
    cd $SCRIPT_DIR/demo;
    python manage.py test;
fi