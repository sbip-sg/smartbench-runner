# Dockerfile for Slither

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

WORKDIR /root/

# Install Slither 0.9.3
RUN pip install slither-analyzer==0.9.3

# Copy executable file
ADD smartbench/tools/slither/run-slither.sh /root/

# Finally, install dependencies that are regularly updated in the last step to
# avoid invalidating Docker cache of previous layers
RUN  pip install git+https://github.com/taquangtrung/solc-detect.git@v0.0.7

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
