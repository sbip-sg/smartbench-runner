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

# Install Go-Ethereum
echo "\nPrepare Golang environments"
GOPATH=$REPO_DIR/go
GOROOT=/usr/lib/go-1.10
echo "GOPATH=$GOPATH"
echo "GOROOT=$GOROOT"
PATH="$GOROOT/bin:$GOPATH/bin:$PATH"

GOETH_DIR="$GOPATH/src/github.com/ethereum/go-ethereum"
echo "\nInstall Go-Ethereum to: $GOETH_DIR"
if [ -d "$GOETH_DIR" ]; then
    echo "Repository $GOETH_DIR already exists!"
    echo "Skip cloning!."
else
    mkdir -p $GOPATH/src/github.com/ethereum
    cd $GOPATH/src/github.com/ethereum
    git clone https://github.com/ethereum/go-ethereum.git
fi

# Cloning ILF source code
TOOL_DIR="$GOPATH/src/$TOOL_ID"
echo "\nCloning $TOOL_NAME source code to: $TOOL_DIR"
if [ -d "$TOOL_DIR" ]; then
    echo "Repository $TOOL_DIR already exists!"
    echo "Skip cloning..."
else
    git clone https://github.com/taquangtrung/ilf $TOOL_DIR
    # git clone https://github.com/eth-sri/ilf $TOOL_DIR
fi

echo "\nApplying IFL patch to Go-Ethereum..."
cd $GOETH_DIR
git checkout 86be91b3e2dff5df28ee53c59df1ecfe9f97e007
git checkout .     # reset all changes
git apply $TOOL_DIR/script/patch.geth

echo "\nInstall ILF Python dependencies"
cd $TOOL_DIR
pip3 install -r requirements.txt

echo "\nBuild Go excution backend"
cd $TOOL_DIR
go build -o execution.so -buildmode=c-shared export/execution.go
