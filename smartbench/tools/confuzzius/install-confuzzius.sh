#!/usr/bin/env sh

# Script to install ConFuzzius tool
# Usage:
#    ./install-confuzzius.sh
# This script is also used in `install_virtual_env` to install `ConFuzzius`
# automatically in `smartbench`

# Prepare repository directory
BASE_DIR=$(dirname "$0")
# echo $BASE_DIR
REPO_DIR=$BASE_DIR"/ConFuzzius"

if [ ! -d "$REPO_DIR" ]; then
    echo "Clone ConFuzzius to $REPO_DIR"
    git clone https://github.com/sbip-sg/ConFuzzius $REPO_DIR
fi

# Set up virtual environment venv
python3 -m venv $BASE_DIR/../../../confuzzius_venv
source $BASE_DIR/../../../confuzzius_venv/bin/activate

# Install requirements
pip install -r $BASE_DIR/ConFuzzius/fuzzer/requirements.txt
