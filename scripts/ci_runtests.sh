#!/usr/bin/env bash

set -e

dirname="$(dirname "$0")"

if [ -n "${TRAVIS_TAG}" ]; then
    PACKAGE_VERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' star_ratings/__init__.py`

    if [ "${TRAVIS_TAG}" != "${PACKAGE_VERSION}" ]; then
        echo "Tag version (${TRAVIS_TAG}) is not equal to the package tag (${PACKAGE_VERSION})"
        exit 1
    fi
fi

. $dirname/runwithcoverage.sh;
. $dirname/runseleniumtests.sh;
