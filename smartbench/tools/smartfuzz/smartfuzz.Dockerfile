# Dockerfile for SmartFuzz

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

ARG GIT_ACCESS_TOKEN         # Github token to be read from --build-arg

# Install PyEVM
WORKDIR /root/
RUN git clone --depth=1 --single-branch --branch fuzzing \
    https://$GIT_ACCESS_TOKEN@github.com/sbip-sg/py-evm.git py-evm
WORKDIR /root/py-evm/
RUN pip3 install -e ./

# Install SmartFuzz
WORKDIR /root/
RUN git clone https://$GIT_ACCESS_TOKEN@github.com/sbip-sg/smart-fuzz smartfuzz
WORKDIR /root/smartfuzz/
RUN pip3 install -r requirements.txt
RUN python scripts/download_solc_compilers.py
# Copy script running Smartfuzz
WORKDIR /root/
ADD smartbench/tools/smartfuzz/run-smartfuzz.sh /root/

# Copy some sample contracts
WORKDIR /root/
RUN mkdir examples
ADD examples/*.sol examples/

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
