#!/bin/bash

# Script to install ConFuzzius tool
#
# Requires Python3.9 to run Confuzzius.
#    sudo add-apt-repository ppa:deadsnakes/ppa
#    sudo apt update
#    sudo apt install python3.9 python3.9-venv
#
# Usage:
#    ./install-confuzzius.sh

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
python -m venv $BASE_DIR/confuzzius_venv
. $BASE_DIR/confuzzius_venv/bin/activate

# Install requirements
pip install -r $TOOL_DIR/fuzzer/requirements.txt

# Install Solc packages
pip install solc-select py-solc --force-reinstall
pip install git+https://github.com/taquangtrung/solc-detect.git --force-reinstall

# Install all Solc compiler by Solc-select
echo $(solc-select install) | sed 's/^.*: //' | xargs solc-select install
