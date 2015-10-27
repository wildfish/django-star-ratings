#!/usr/bin/env bash
dirname="$(dirname "$0")"
coverage run --source="$dirname/../star_ratings" "$dirname/runtests.py" && coverage report -m
