#!/usr/bin/env sh

# Script to install tool
# Usage:
#    ./install-ilf.sh

# Tool settings
TOOL_NAME="ILF"
TOOL_ID="ilf"

# Prepare repository directory
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
    git clone https://github.com/taquangtrung/ilf $TOOL_DIR
    # git clone https://github.com/eth-sri/ilf $TOOL_DIR
fi

# Install ILF using Docker
cd $TOOL_DIR
docker build -t ilf .
