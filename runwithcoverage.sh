#!/usr/bin/env bash
dirname="$(dirname "$0")"
coverage run --source="$dirname/wildfish_ratings" "$dirname/runtests.py" && coverage report -m
