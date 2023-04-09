#!/usr/bin/bash

# Usage:
#   ./run-slither.sh <test-file> [additional-slither-arguments]
#
# NOTE:
#   - Test file must be the first argument
#   - This script must be configured so that it can be used both to run
#     in a Docker container as well as to run locally.
#


# Arguments of Slither
TEST_FILE=$(realpath $1)
ADDITIONAL_ARGS=${@:2}

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Run Slither
SOLC_VERSION=$SOLC_VER slither $TEST_FILE $ADDITIONAL_ARGS
