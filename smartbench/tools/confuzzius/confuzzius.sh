#!/usr/bin/bash

# Configure venv
source confuzzius_venv/bin/activate

# Run Smartbench
python ConFuzzius/fuzzer/main.py $@
