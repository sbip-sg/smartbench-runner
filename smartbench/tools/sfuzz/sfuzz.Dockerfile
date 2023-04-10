# Dockerfile for sFuzz

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

# Install sFuzz dependencies
RUN apt -y install cmake libleveldb-dev

# Install sFuzz
WORKDIR /root/
RUN git clone --recursive https://github.com/thanhtoantnt/sFuzz.git sfuzz
WORKDIR /root/sfuzz
RUN mkdir -p build; cd build; cmake ..
WORKDIR /root/sfuzz/build/fuzzer
RUN make

# Copy executable file
# ADD smartbench/tools/sfuzz/run-sfuzz.sh /root/

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
