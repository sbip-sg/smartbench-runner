# Dockerfile for Mythril

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

# Install mythril
WORKDIR /root/
RUN pip install mythril

# Copy script running Mythril
ADD smartbench/tools/mythril/run-mythril.sh /root/

# Copy some sample contracts
WORKDIR /root/
RUN mkdir examples
ADD examples/*.sol examples/

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
