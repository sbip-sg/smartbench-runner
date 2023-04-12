#!/usr/bin/bash

# Configure directories
BASE_DIR=$(pwd)
SMARTBENCH_ROOT=$(realpath $(dirname "$0"))

# Configure virtual environment venv
cd $SMARTBENCH_ROOT
. venv/bin/activate

# Run Smartbench
cd $BASE_DIR
PYTHONPATH=$SMARTBENCH_ROOT python -m smartbench.smartbench $@

# Deactivate virtual environment
deactivate
