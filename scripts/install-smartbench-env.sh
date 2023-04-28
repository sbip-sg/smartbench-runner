#!/bin/bash

# Usage:
#   cd smartbench-runner
#   ./scripts/install-smartbench-env.sh

SCRIPT_DIR=$(realpath $(dirname "$0"))
SMARTBENCH_ROOT=$(dirname $SCRIPT_DIR)
BIN_DIR="$SMARTBENCH_ROOT/bin"

# Set up virtual environment venv
python3 -m venv venv
source venv/bin/activate

# Or run `source venv/bin/activate.fish` if using Fish shell.
# source venv/bin/activate.fish

# Install requirements
pip install -r $SMARTBENCH_ROOT/requirements.txt

# Install all missing Solc compilers
for v in $(echo $(solc-select install) | sed 's/^.*://'); do
    solc-select install $v;
done

# Install binary utilities
mkdir -p $BIN_DIR
cd $BIN_DIR
if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    wget https://github.com/taquangtrung/smartbench-binaries/raw/main/solquery/solquery-linux-x86-64 \
        -O solquery
    chmod u+x solquery
elif [ "$(uname)" == "Darwin" ]; then
    wget https://github.com/taquangtrung/smartbench-binaries/raw/main/solquery/solquery-darwin \
        -O solquery
    chmod u+x solquery
fi
