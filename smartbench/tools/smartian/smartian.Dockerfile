# Dockerfile for Smartian

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

WORKDIR /root/

# Clone Smartian source code
RUN git clone https://github.com/sbip-sg/Smartian smartian
WORKDIR /root/smartian
RUN git submodule update --init --recursive

# Install Smartian dependencies
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb \
    -O packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt-get update
RUN apt-get install -y apt-transport-https dotnet-sdk-5.0

# Compile Smartian
WORKDIR /root/smartian
RUN make

# Copy executable file
WORKDIR /root/
ADD smartbench/tools/smartian/run-smartian.sh /root/

# Finally, install dependencies that are regularly updated in the last step to
# avoid invalidating Docker cache of previous layers
RUN pip install git+https://github.com/taquangtrung/solc-detect.git@v0.0.7

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]
