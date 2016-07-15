#!/usr/bin/env bash

dirname="$(dirname "$0")"

. $dirname/runwithcoverage.sh;
. $dirname/runseleniumtests.sh;
