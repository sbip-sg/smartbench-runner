#!/bin/bash

# Usage:
#   cd smartbench-runner
#   ./install.sh

BASEDIR=$(dirname "$0")

# Set up virtual environment venv
python3 -m venv confuzzius_venv
source confuzzius_venv/bin/activate

# Install requirements
pip install -r $BASEDIR/../../../ConFuzzius/fuzzer/requirements.txt
