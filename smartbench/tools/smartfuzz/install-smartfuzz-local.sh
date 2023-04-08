#!/bin/bash

#    ./install-confuzzius-local.sh

# Tool settings
TOOL_NAME="SmartFuzz"
TOOL_ID="smartfuzz"
TOOL_VENV="${TOOL_ID}_venv"

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
    git clone git@github.com:sbip-sg/smart-fuzz $TOOL_DIR
fi

# Set up virtual environment venv
python -m venv $BASE_DIR/$TOOL_VENV
. $BASE_DIR/$TOOL_VENV/bin/activate

# Install requirements
pip install -r $TOOL_DIR/requirements.txt

# Install Solc packages
pip install solc-select py-solc --force-reinstall
pip install git+https://github.com/taquangtrung/solc-detect.git --force-reinstall

# Install all Solc compiler by Solc-select
echo $(solc-select install) | sed 's/^.*: //' | xargs solc-select install
