#!/usr/bin/env sh

# Script to install ToolName tool
# Usage:
#    ./install-toolname.sh

# Prepare repository directory
BASE_DIR=$(dirname "$0")
REPO_DIR=$BASE_DIR"/repo/toolname"
mkdir -p $REPO_DIR

git clone https://github.com/tool/toolname $REPO_DIR
