#!/usr/bin/env bash

set -e

dirname="$(dirname "$0")"

. $dirname/runwithcoverage.sh;
. $dirname/runseleniumtests.sh;
