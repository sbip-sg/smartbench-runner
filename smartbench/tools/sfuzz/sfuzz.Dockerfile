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

# Add template files required by sFuzz for experiment
RUN rm -rf output
RUN mkdir -p output
WORKDIR /root/sfuzz/build/fuzzer
RUN cp ../../assets . -r
RUN cp ~/.solc-select/artifacts/solc-0.4.16/solc-0.4.16 /bin/

# Copy executable file
WORKDIR /root/
ADD smartbench/tools/sfuzz/run-sfuzz.sh /root/

# Finally, install dependencies that are regularly updated in the last step to
# avoid invalidating Docker cache of previous layers
RUN pip install git+https://github.com/taquangtrung/solc-detect.git@v0.0.7

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
