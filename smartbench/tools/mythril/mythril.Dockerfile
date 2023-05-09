# Dockerfile for Mythril

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

# Install mythril
WORKDIR /root/
RUN pip install mythril

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
