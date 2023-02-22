#!/bin/bash

# Usage:
#   cd smartbench-runner
#   ./install/setup-venv.sh

BASEDIR=$(dirname "$0")

# Set up virtual environment venv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r $BASEDIR/requirements.txt
