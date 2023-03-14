#!/usr/bin/bash

# Configure venv
source confuzzius_venv/bin/activate

# Run Smartbench
python smartbench/tools/confuzzius/ConFuzzius/fuzzer/main.py $@
