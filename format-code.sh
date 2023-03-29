#!/usr/bin/env sh

BASEDIR=$(dirname "$0")

echo "Running isort..."
isort $BASEDIR/smartbench/

echo "Running black..."
black $BASEDIR/smartbench/
