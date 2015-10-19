#!/usr/bin/env bash

SCRIPT_DIR=`dirname "${BASH_SOURCE[0]}"`


if [ "$TRAVIS_PULL_REQUEST" == true ] || [ "$1" == "-f" ]; then
    cd $SCRIPT_DIR/demo;
    python manage.py test;
fi