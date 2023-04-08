# Dockerfile for Confuzzius

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

WORKDIR /root/

# Install Confuzzius
ENV TOOL_DIR=confuzzius
RUN git clone https://github.com/christoftorres/ConFuzzius $TOOL_DIR
RUN pip install -r $TOOL_DIR/fuzzer/requirements.txt

# Copy executable file
ADD smartbench/tools/confuzzius/run-confuzzius.sh /root/

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]
