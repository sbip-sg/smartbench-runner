# Dockerfile for Slither

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

WORKDIR /root/

# Install Slither 0.9.3
RUN pip install slither-analyzer==0.9.3

# Update additional utilities to the newest version
RUN pip install git+https://github.com/taquangtrung/solc-detect.git --force-reinstall

# Copy executable file
ADD smartbench/tools/slither/run-slither.sh /root/

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]
