# Dockerfile for Slither 0.9.3

FROM ubuntu:20.04

# Update working directory to $HOME (default to `/root` in Ubuntu Docker image)
WORKDIR /root/

# Install Ubuntu packages
RUN apt-get update
RUN apt-get install -y python3 python-is-python3 python3-pip

# Install Solc-select and all Solc compilers
RUN pip install solc-select
RUN echo $(solc-select install) | sed 's/^.*: //' | xargs solc-select install

# Install Slither 0.9.3
RUN pip install solc-select slither-analyzer==0.9.3
