#!/usr/bin/env sh

# Script to install Smartian
# Usage:
#    ./install-smartian-manual.sh

# Tool settings
TOOL_NAME="Smartian"
TOOL_ID="smartian"

# Prepare repository directory
echo "Preparing Smartian repo directories..."
BASE_DIR=$(dirname "$0")
BASE_DIR=$(cd $BASE_DIR; pwd)       # convert to absolute path.
REPO_DIR=$BASE_DIR"/repo"
mkdir -p $REPO_DIR
echo "Root repo dir: $REPO_DIR"

# Cloning Smartian source code
TOOL_DIR="$REPO_DIR/$TOOL_ID"
echo "\nCloning $TOOL_NAME source code to: $TOOL_DIR"
if [ -d "$TOOL_DIR" ]; then
    echo "Repository $TOOL_DIR already exists!"
    echo "Skip cloning..."
else
    git clone https://github.com/sbip-sg/Smartian $TOOL_DIR
fi

# Compiling Smartian
cd $TOOL_DIR
echo "\nUpdating sub-modules..."
git submodule update --init --recursive
make

# Install environment
echo "\nInstall Dotnet 5 SDK"
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb \
    -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y apt-transport-https
sudo apt-get update
sudo apt-get install -y dotnet-sdk-5.0

# Install environment
echo "\nCompiling Smartian"
cd $TOOL_DIR
git submodule update --init --recursive
make
