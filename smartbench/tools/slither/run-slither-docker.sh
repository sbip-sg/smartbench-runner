#!/bin/bash

# This script run Slither in a Docker container.

# Arguments of Slither
TEST_FILE=$(realpath $1)
OTHER_ARGS=${@:2}

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Run Slither
SOLC_VERSION=$SOLC_VER slither $TEST_FILE $OTHER_ARGS


# Run Slither
docker exec -it
