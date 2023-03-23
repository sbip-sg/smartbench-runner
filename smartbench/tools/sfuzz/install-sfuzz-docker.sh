#!/usr/bin/env sh

# Script to install sFuzz Docker
# Usage:
#    ./install-sfuzz-docker.sh

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
    git clone --recursive git@github.com:thanhtoantnt/sFuzz.git $TOOL_DIR
fi

# Installing sFuzz using Docker
echo "\nBuild sFuzz Docker"
cd $TOOL_DIR
docker build -t sfuzz .
