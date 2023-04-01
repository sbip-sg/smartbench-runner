#!/bin/bash

# This script is call inside `confuzzius.py` to run `ConFuzzius` with an input file.

# Arguments of Confuzzius
TEST_FILE=$(realpath $1)
OTHER_ARGS=${@:2}

# Tool settings
TOOL_ID="confuzzius"

# Prepare repository directory
TOOL_DIR=$(realpath $(dirname "$0"))
TOOL_SRC_DIR=$TOOL_DIR"/repo/confuzzius"

# Configure venv
. $TOOL_DIR/confuzzius_venv/bin/activate

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Run Confuzzius
SOLC_VERSION=$SOLC_VER python $TOOL_SRC_DIR/fuzzer/main.py --evm byzantium -s $TEST_FILE $OTHER_ARGS
