#!/usr/bin/sh

# Configure virtual environment venv
. venv/bin/activate

# Run Smartbench
python -m smartbench.smartbench $@

# Deactivate virtual environment
deactivate
