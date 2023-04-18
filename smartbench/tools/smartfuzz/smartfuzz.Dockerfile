# Dockerfile for SmartFuzz

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

ARG GIT_ACCESS_TOKEN         # Github token to be read from --build-arg

WORKDIR /root/

# Install PyEVM
RUN git clone --depth=1 --single-branch --branch fuzzing \
    https://$GIT_ACCESS_TOKEN@github.com/sbip-sg/py-evm.git py-evm
WORKDIR /root/py-evm/
RUN pip3 install -e ./

# Install SmartFuzz
WORKDIR /root/
RUN git clone https://$GIT_ACCESS_TOKEN@github.com/sbip-sg/smart-fuzz smartfuzz
WORKDIR /root/smartfuzz/
RUN pip3 install -r requirements.txt

# Copy executable file
WORKDIR /root/
ADD smartbench/tools/smartfuzz/run-smartfuzz.sh /root/

# Finally, install dependencies that are regularly updated in the last step to
# avoid invalidating Docker cache of previous layers
RUN pip install git+https://github.com/taquangtrung/solc-detect.git@v0.0.7

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]
