# Dockerfile for Smartian

FROM ubuntu:20.04

# Some build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Asia/Singapore

# Update working directory to $HOME (default to `/root` in Ubuntu Docker image)
WORKDIR /root/

# Install Ubuntu packages
RUN apt-get update
RUN apt-get -y install git tzdata

# Install Python3
RUN apt-get install -y python3 python-is-python3 python3-pip wget

# Install Solc-select and all Solc compilers
RUN pip install solc-select
RUN for v in $(echo $(solc-select install) | sed 's/^.*: //'); do solc-select install $v; done

# Install Solc libraries
RUN pip install py-solc --force-reinstall
RUN pip install git+https://github.com/taquangtrung/solc-detect.git --force-reinstall

# Install Smartian
ENV TOOL_DIR=/root/smartian
RUN git clone https://github.com/sbip-sg/Smartian $TOOL_DIR
WORKDIR $TOOL_DIR
RUN git submodule update --init --recursive

# Install environment
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb \
    -O packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN apt-get update
RUN apt-get install -y dotnet-sdk-5.0

# Compile Smartian
WORKDIR $TOOL_DIR
RUN make

# Prepare testing environments
WORKDIR /root/
RUN mkdir examples
ADD examples/*.sol examples/

# Prepare benchmarking environments
RUN mkdir benchmarks
RUN mkdir results

# Copy executable file
ADD smartbench/tools/smartian/run-smartian.sh /root/

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
