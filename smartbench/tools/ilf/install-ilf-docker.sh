#!/usr/bin/env sh

# Script to install tool
# Usage:
#    ./install-ilf.sh

# Tool settings
TOOL_NAME="ILF"
TOOL_ID="ilf"

# Prepare repository directory
echo "Preparing ILF repo directories..."
BASE_DIR=$(dirname "$0")
BASE_DIR=$(cd $BASE_DIR; pwd)       # convert to absolute path.
REPO_DIR=$BASE_DIR"/repo"
mkdir -p $REPO_DIR
echo "Root repo dir: $REPO_DIR"

# Prepare tool directory
echo "Preparing tool directory..."
TOOL_DIR=$REPO_DIR/$TOOL_ID

# Cloning ILF source code
TOOL_DIR="$GOPATH/src/$TOOL_ID"
echo "\nCloning $TOOL_NAME source code to: $TOOL_DIR"
if [ -d "$TOOL_DIR" ]; then
    echo "Repository $TOOL_DIR already exists!"
    echo "Skip cloning!"
else
    git clone https://github.com/taquangtrung/ilf $TOOL_DIR
    # git clone https://github.com/eth-sri/ilf $TOOL_DIR
fi

# Install ILF using Docker
echo "\nBuild ILF Docker..."
cd $TOOL_DIR
docker build -t ilf .
