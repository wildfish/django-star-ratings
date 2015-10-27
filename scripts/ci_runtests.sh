#!/usr/bin/env bash

dirname="$(dirname "$0")"

if [ "$RUN_WEB_TESTS" = "false" ]; then
    . $dirname/runwithcoverage.sh;
else
    . $dirname/runseleniumtests.sh -f;
fi
