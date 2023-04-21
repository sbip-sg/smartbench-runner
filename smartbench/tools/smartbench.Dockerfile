# Dockerfile for base image of all analysis tools

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

FROM ubuntu:20.04

# Some build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Asia/Singapore

# Update working directory to $HOME (default to `/root` in Ubuntu Docker image)
WORKDIR /root/

# Install Ubuntu packages
RUN apt-get update
RUN apt-get -y install git wget tzdata

# Install Python3.9
RUN apt-get install -y python3.9 python3.9-dev python-is-python3 python3-pip
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3
RUN pip install --upgrade pip

# Install Solc-select and all Solc compilers
RUN pip install solc-select
RUN for v in $(echo $(solc-select install) | sed 's/^.*: //'); do solc-select install $v; done

# Install Solc libraries
RUN pip install py-solc --force-reinstall
RUN pip install git+https://github.com/taquangtrung/solc-detect.git@v0.0.7

# Prepare benchmarking environments
RUN mkdir benchmarks
RUN mkdir results

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
