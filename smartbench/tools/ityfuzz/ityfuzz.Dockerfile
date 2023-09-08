# Dockerfile for ItyFuzz

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM ubuntu:22.04

# Some build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Asia/Singapore

# Update working directory to $HOME (default to `/root` in Ubuntu Docker image)
WORKDIR /root/

# Install Ubuntu packages
RUN apt update
RUN apt -y install git wget tzdata
RUN apt -y install vim

# Install Python3.9
RUN apt-get install -y python3.9 python3-pip python-is-python3
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3

# Prepare benchmarking environments
RUN mkdir benchmarks
RUN mkdir testing
RUN mkdir results

# Update default packages
RUN apt-get update

# Get Ubuntu packages
RUN apt-get install -y \
    build-essential \
    curl

# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install ItyFuzz
WORKDIR /root/
RUN git clone --recursive https://github.com/fuzzland/ityfuzz.git && cd ityfuzz && git checkout stable

WORKDIR /root/ityfuzz/cli
RUN apt-get install -y pkg-config libssl-dev cmake libclang-dev
RUN rustup default nightly-2023-04-10
# RUN cargo build --release
# RUN cargo +nightly build --release

# Install Solc-select and all Solc compilers
# RUN pip3 install solc-select
# RUN for v in $(echo $(solc-select install) | sed 's/^.*: //'); do solc-select install $v; done

# Install Solc libraries
# RUN pip install py-solc --force-reinstall

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]