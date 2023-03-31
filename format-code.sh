#!/usr/bin/env sh

BASEDIR=$(dirname "$0")

echo "Running isort..."
isort $(git ls-files '*.py')

echo "Running black..."
black $(git ls-files '*.py')
