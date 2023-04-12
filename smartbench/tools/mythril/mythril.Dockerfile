# Dockerfile for Mythril

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

WORKDIR /root/

# Copy executable file
ADD smartbench/tools/mythril/run-mythril.sh /root/

# Install mythril
RUN pip install mythril

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]