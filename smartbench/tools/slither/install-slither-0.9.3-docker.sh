#!/usr/bin/env sh

# Usage:
#    ./install-slither-0.9.3-docker.sh

# Prepare repository directory
BASE_DIR=$(dirname "$0")
cd $BASE_DIR

# Prepare some examples
mkdir examples
cp ../../../examples/*.sol examples

# Run Docker
docker build -f slither_0.9.3.dockerfile -t slither:0.9.3 .

# Clean examples
rm -rf examples
