# Dockerfile for Confuzzius

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

# Install ConFuzzius
WORKDIR /root/
RUN git clone https://github.com/christoftorres/ConFuzzius confuzzius
WORKDIR /root/confuzzius
RUN pip install -r fuzzer/requirements.txt

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
