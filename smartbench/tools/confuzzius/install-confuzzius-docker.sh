#!/usr/bin/env sh

# Usage: install-confuzzius-docker.sh <args-to-docker-build>
#  - 
#    ./install-confuzzius-docker.sh --no-cache


# Prepare repository directory
BASE_DIR=$(dirname "$0")
cd $BASE_DIR

# Prepare some examples
mkdir examples
cp ../../../examples/*.sol examples

# Build a fresh Docker imagex
docker build -f confuzzius.dockerfile -t confuzzius . $@

# Clean after installation
rm -rf examples
