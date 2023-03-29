#!/usr/bin/bash
TOOL_ID="smartfuzz"

# Prepare repository directory
BASE_DIR=$(dirname "$0")
REPO_DIR=$BASE_DIR"/repo"
TOOL_DIR=$REPO_DIR/$TOOL_ID

# Run Smartbench
python $TOOL_DIR/benchmark.py $@
