#!/usr/bin/env sh

# Usage:
#    ./install-slither-0.9.3-docker.sh

# Prepare repository directory
BASE_DIR=$(dirname "$0")

cd $BASE_DIR
docker build -f Slither_0.9.3.Dockerfile -t slither .
