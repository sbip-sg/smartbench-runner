# Dockerfile for ItyFuzz

FROM rust:buster as run_environment
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-venv libz3-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
RUN mkdir /bins

FROM run_environment as build_environment
RUN apt-get update && apt-get install -y clang pkg-config cmake \
    && rm -rf /var/lib/apt/lists/*

# Install ItyFuzz
WORKDIR /root/
RUN git clone --recursive https://github.com/fuzzland/ityfuzz.git && cd ityfuzz && git checkout stable

WORKDIR /root/ityfuzz/cli
RUN cargo build --release

# Entry point when running the container as an executable
WORKDIR /root/

# Prepare benchmarking environments
RUN mkdir benchmarks
RUN mkdir testing
RUN mkdir results

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
