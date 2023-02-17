#!/bin/bash

# This file sets up the Python virtual environemnt (venv) for Smartbench.


# tested for python >= 3.6.9
# python < 3.10 will give an error when using the ':'-feature in input patterns
python3 -m venv venv
source venv/bin/activate

# avoid spurious errors/warnings; the next two lines could be omitted
pip install --upgrade pip
pip install wheel

# Install PIP packages neededx
pip install pyyaml colorama requests semantic_version docker py-cpuinfo solc_select

# Install additional packages
pip install git+https://github.com/sbip-sg/solc-detect.git@main#egg=solc_detect
