#!/usr/bin/bash

# Configure venv
source confuzzius_venv/bin/activate

# Run Smartbench
python -m smartbench.smartbench $@
