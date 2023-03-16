#!/usr/bin/env sh

# This script is call inside `confuzzius.py` to run `ConFuzzius` with an input file.

# Prepare repository directory
BASE_DIR=$(dirname "$0")

# Configure venv
source $BASE_DIR/../../../confuzzius_venv/bin/activate

# Run Smartbench
python $BASE_DIR/ConFuzzius/fuzzer/main.py $@
