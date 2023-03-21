#!/usr/bin/env sh

# Script to install sFuzz
# Usage:
#    ./install-sfuzz.sh

# Tool settings
TOOL_NAME="sFuzz"
TOOL_ID="sfuzz"

# Prepare repository directory
echo "Preparing repository directory..."
FILE_PATH=$(realpath "$0")
BASE_DIR=$(dirname "$FILE_PATH")
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
    git clone --recursive https://github.com/thanhtoantnt/sFuzz $TOOL_DIR
fi

# Installing tool
echo "Compiling $TOOL_NAME..."
cd $TOOL_DIR
mkdir -p build
cd build
cmake ../
cd fuzzer
make

# Add
rm -rf assets
mkdir assets
rm -rf output
mkdir -p output
cd assets
cp $BASE_DIR"/NormalAttacker.sol" .
cp $BASE_DIR"/ReentrancyAttacker.sol" .
