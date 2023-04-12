#!/bin/bash

# Usage:
#   ./run-ilf.sh <test-file> <additional arguments>
#
# NOTE:
#   - Test file must be the first argument
#   - This script must be configured so that it can be used both to run
#     in a Docker container as well as to run locally.
#

# Arguments of Ilf
TEST_FILE=$(realpath $1)
OTHER_ARGS=${@:2}

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    TOOL_ROOT_PATH="/root/go/src/ilf"
else
    TOOL_ROOT_PATH="$(realpath $(dirname "$0"))/repo/go/src/ilf"
fi

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)
