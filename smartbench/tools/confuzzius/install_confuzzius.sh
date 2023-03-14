#!/bin/bash

# Set up virtual environment venv
python3 -m venv confuzzius_venv
source confuzzius_venv/bin/activate

# Install requirements
pip install -r smartbench/tools/confuzzius/ConFuzzius/fuzzer/requirements.txt
