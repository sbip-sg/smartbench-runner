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
