#!/bin/bash

# Script to install ConFuzzius tool
# Usage:
#    ./install-confuzzius.sh
# This script is also used in `install_virtual_env` to install `ConFuzzius`
# automatically in `smartbench`

# Tool settings
TOOL_NAME="confuzzius"
TOOL_ID="confuzzius"

# Prepare repository directory
# Prepare repository directory
echo "Preparing repository directory..."
BASE_DIR=$(dirname "$0")
REPO_DIR=$BASE_DIR"/repo"
mkdir -p $REPO_DIR

# Prepare tool directory
echo "Preparing tool directory..."
TOOL_DIR=$REPO_DIR/$TOOL_ID

# Cloning tool source code
echo "Cloning $TOOL_NAME source code to: $TOOL_DIR"
if [ -d "$TOOL_DIR" ]; then
    echo "Repository $TOOL_DIR already exists!"
    echo "Skip cloning..."
else
    git clone https://github.com/sbip-sg/ConFuzzius $TOOL_DIR
fi

# Set up virtual environment venv
python3 -m venv $BASE_DIR/confuzzius_venv
source $BASE_DIR/confuzzius_venv/bin/activate

# Install requirements
pip install -r $TOOL_DIR/fuzzer/requirements.txt

# Install additional packages
pip install 'py-solc-x==1.1.1' --force-reinstall
