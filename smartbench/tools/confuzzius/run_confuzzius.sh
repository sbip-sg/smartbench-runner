#!/bin/bash

# This script is call inside `confuzzius.py` to run `ConFuzzius` with an input file.

# Tool settings
TOOL_ID="confuzzius"

# Prepare repository directory
BASE_DIR=$(dirname "$0")
REPO_DIR=$BASE_DIR"/repo"
TOOL_DIR=$REPO_DIR/$TOOL_ID

# Configure venv
. $BASE_DIR/confuzzius_venv/bin/activate

# Run Confuzzius
python $TOOL_DIR/fuzzer/main.py $@
