#!/usr/bin/env bash

if [ "$RUN_WEB_TESTS" = "false" ]; then
    ./runwithcoverage.sh;
else
    ./runseleniumtests.sh -f;
fi
