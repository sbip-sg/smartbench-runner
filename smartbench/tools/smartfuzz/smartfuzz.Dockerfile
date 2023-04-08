# Dockerfile for SmartFuzz

FROM ubuntu:20.04

# Some build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Asia/Singapore
ARG GIT_ACCESS_TOKEN         # Github token to be read from --build-arg

# Update working directory to $HOME (default to `/root` in Ubuntu Docker image)
WORKDIR /root/

# Install Ubuntu packages
RUN apt-get update
RUN apt-get -y install git tzdata

# Install Python3.9
RUN apt-get install -y python3.9 python3.9-dev python-is-python3 python3-pip
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3
RUN pip install --upgrade pip
# Install Solc-select and all Solc compilers
RUN pip install solc-select
# RUN for v in $(echo $(solc-select install) | sed 's/^.*: //'); do solc-select install $v; done

# Install Solc libraries
RUN pip install py-solc --force-reinstall
RUN pip install git+https://github.com/taquangtrung/solc-detect.git --force-reinstall

# Install py-evm
WORKDIR /root/
RUN git clone --depth=1 --single-branch --branch fuzzing \
    https://$GIT_ACCESS_TOKEN@github.com/sbip-sg/py-evm.git /root/py-evm
WORKDIR /root/py-evm/
# RUN pip3 install -e ./

# Install SmartFuzz
WORKDIR /root/
ENV TOOL_DIR=smartfuzz
RUN git clone https://$GIT_ACCESS_TOKEN@github.com/sbip-sg/smart-fuzz $TOOL_DIR
WORKDIR /root/smartfuzz
RUN pip3 install -r requirements.txt
RUN python scripts/download_solc_compilers.py
# Prepare testing environments
RUN mkdir examples
ADD examples/*.sol examples/

# Prepare benchmarking environments
RUN mkdir benchmarks
RUN mkdir results

# Copy executable file
ADD run-smartfuzz.sh /root/

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]
