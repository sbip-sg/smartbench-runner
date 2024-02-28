# Dockerfile for Mythril

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

WORKDIR /root/

# Install Ubuntu packages
RUN apt -y install libssl-dev python3-dev python3-pip curl

# Install Rust, which is required by Mythril
ENV CARGO_UNSTABLE_SPARSE_REGISTRY=true
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH=/root/.cargo/bin:$PATH

# Install the latest version of Mythril
RUN pip3 install mythril

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
