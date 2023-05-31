# Dockerfile for Confuzzius

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest
RUN apt update
# Install ConFuzzius customized by SBIP
WORKDIR /root/
RUN git clone https://github.com/taquangtrung/ConFuzzius confuzzius
WORKDIR /root/confuzzius
RUN pip install -r fuzzer/requirements.txt

# Copy script running ConFuzzius
# ADD smartbench/tools/confuzzius/run-confuzzius.sh /root/

# Copy some sample contracts
WORKDIR /root/
RUN mkdir examples
ADD examples/*.sol examples/

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
