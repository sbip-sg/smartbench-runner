#!/bin/bash

# Usage:
#   ./run-smartfuzz.sh <test-file> <additional arguments>
#
# NOTE:
#   - Test file must be the first argument
#   - This script must be configured so that it can be used both to run
#     in a Docker container as well as to run locally.
#

# Arguments of SmartFuzz
TEST_FILE=$(realpath $1)
OTHER_ARGS=${@:2}

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    TOOL_ROOT_PATH="/root/smartfuzz"
else
    TOOL_ROOT_PATH="$(realpath $(dirname "$0"))/repo/smartfuzz"
fi

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Run SmartFuzz
SOLC_VERSION=$SOLC_VER python "$TOOL_ROOT_PATH/main.py" \
    $TEST_FILE $OTHER_ARGS
