#!/usr/bin/env sh

# Script to install ToolName tool
# Usage:
#    ./install-toolname.sh

# Tool setting
TOOL_NAME="tool-name"

# Prepare repository directory
BASE_DIR=$(dirname "$0")
REPO_DIR=$BASE_DIR"/repo"
mkdir -p $REPO_DIR

# Cloning tool source code:
TOOL_DIR=$REPO_DIR/$TOOL_NAME
echo "Cloning IFL source code to: "$TOOL_DIR
if [ -d "$TOOL_DIR" ]; then
    echo "Error: directory $TOOL_DIR already exists!"
    echo "Quit installation..."
    exit 1
else
    git clone https://github.com/tool/tool-name $TOOL_DIR
fi
