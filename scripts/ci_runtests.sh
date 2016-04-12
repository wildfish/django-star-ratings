#!/usr/bin/env bash

dirname="$(dirname "$0")"

if [ "$RUN_WEB_TESTS" = "false" ] || [ ! "${TRAVIS_PULL_REQUEST}" = "false" ]; then
    . $dirname/runwithcoverage.sh;
else
    . $dirname/runseleniumtests.sh;
fi
