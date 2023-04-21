# Dockerfile for Slither

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

# Install Slither 0.9.3
WORKDIR /root/
RUN pip install slither-analyzer==0.9.3

# Copy script running Slither
ADD smartbench/tools/slither/run-slither.sh /root/

# Copy some sample contracts
WORKDIR /root/
RUN mkdir examples
ADD examples/*.sol examples/

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
