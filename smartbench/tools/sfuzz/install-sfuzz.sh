#!/usr/bin/env sh

# Script to install sFuzz
# Usage:
#    ./install-sfuzz.sh

TOOL_NAME="sFuzz"
TOOL_ID="sfuzz"

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
    git clone --recursive https://github.com/duytai/sFuzz $TOOL_DIR
fi

# Installing too
echo "Compiling $TOOL_NAME..."
cd $TOOL_DIR
mkdir build
cd build
cmake ../
make
