#!/bin/bash

# Usage:
#   ./run-confuzzius.sh <test-file> <additional arguments>
#
# NOTE:
#   - Test file must be the first argument
#   - This script must be configured so that it can be used both to run
#     in a Docker container as well as to run locally.
#

# Arguments of Confuzzius
TEST_FILE=$(realpath $1)
OTHER_ARGS=${@:2}

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    $TOOL_PATH="/root/confuzzius"
else
    $TOOL_PATH="$(realpath $(dirname "$0"))/repo/confuzzius"
fi

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Run Confuzzius
SOLC_VERSION=$SOLC_VER python /root/confuzzius/fuzzer/main.py \
    --evm byzantium \
    -s $TEST_FILE $OTHER_ARGS
