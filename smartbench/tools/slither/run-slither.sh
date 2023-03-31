#!/usr/bin/bash

# Usage:
#   ./run-slither.sh <test-file> <additional arguments>
#
# NOTE: test file must be the first argument

TEST_FILE=$(realpath $1)
SLITHER_ARGS=${@:2}

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Run Slither
SOLC_VERSION=$SOLC_VER slither $TEST_FILE $SLITHER_ARGS
