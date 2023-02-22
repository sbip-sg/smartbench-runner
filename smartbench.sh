#!/usr/bin/bash

# Configure venv
source venv/bin/activate

# Run Smartbench
python -m smartbench.smartbench $@
