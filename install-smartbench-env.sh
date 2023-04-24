#!/bin/bash

# Usage:
#   cd smartbench-runner
#   ./install.sh

BASEDIR=$(dirname "$0")

# Set up virtual environment venv
python3 -m venv venv
source venv/bin/activate

# Or run `source venv/bin/activate.fish` if using Fish shell.
# source venv/bin/activate.fish

# Install requirements
pip install -r $BASEDIR/requirements.txt

# Install all missing Solc compilers
for v in $(echo $(solc-select install) | sed 's/^.*://'); do
    solc-select install $v;
done

# Install utilities
cd $BASEDIR
if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    wget https://github.com/taquangtrung/smartbench-binaries/raw/main/solquery/solquery-linux-x86-64 \
        -O solquery
    chmod u+x solquery
elif [ "$(uname)" == "Darwin" ]; then
    wget https://github.com/taquangtrung/smartbench-binaries/raw/main/solquery/solquery-darwin \
        -O solquery
    chmod u+x solquery
fi
