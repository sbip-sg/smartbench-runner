#!/usr/bin/bash

# Configure virtual environment venv
source venv/bin/activate

# Run Smartbench
python -m smartbench.smartbench $@

# Deactivate virtual environment
deactivate
