#!/usr/bin/env sh

# Script to install Mythril tool
# Usage:
#    ./install-mythril.sh

# Prepare repository directory
BASE_DIR=$(dirname "$0")

source $BASE_DIR/../../../venv/bin/activate
pip3 install mythril
