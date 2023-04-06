# Dockerfile for Slither 0.9.3

FROM ubuntu:20.04

# Update working directory to $HOME (default to `/root` in Ubuntu Docker image)
WORKDIR /root/

# Install Ubuntu packages
RUN apt-get update
RUN apt-get install -y git python3 python-is-python3 python3-pip

# Install Solc-select and all Solc compilers
RUN pip install solc-select
RUN for v in $(echo $(solc-select install) | sed 's/^.*: //'); do solc-select install $v; done

# Install Solc libraries
RUN pip install git+https://github.com/taquangtrung/solc-detect.git --force-reinstall

# Install Slither 0.9.3
RUN pip install solc-select slither-analyzer==0.9.3

# Prepare testing environments
RUN mkdir examples
ADD examples/*.sol examples/

# Prepare benchmarking environments
RUN mkdir benchmarks
RUN mkdir results

# Copy executable file
ADD run-slither.sh /root/

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]
