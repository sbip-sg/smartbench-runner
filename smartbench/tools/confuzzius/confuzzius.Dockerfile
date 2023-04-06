# Dockerfile for Confuzzius

FROM ubuntu:20.04

# Update working directory to $HOME (default to `/root` in Ubuntu Docker image)
WORKDIR /root/

# Install Ubuntu packages
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive TZ=Asia/Singapore apt-get -y install git tzdata

# Install Python3
RUN apt-get install -y python3 python-is-python3 python3-pip

# Install Solc-select and all Solc compilers
RUN pip install solc-select
RUN for v in $(echo $(solc-select install) | sed 's/^.*: //'); do solc-select install $v; done

# Install Solc libraries
RUN pip install py-solc --force-reinstall
RUN pip install git+https://github.com/taquangtrung/solc-detect.git --force-reinstall

# Install Confuzzius
ENV CONFUZZIUS_DIR=confuzzius
RUN git clone https://github.com/christoftorres/ConFuzzius $CONFUZZIUS_DIR
RUN pip install -r $CONFUZZIUS_DIR/fuzzer/requirements.txt

# Prepare testing environments
RUN mkdir examples
ADD examples/*.sol examples/

# Prepare benchmarking environments
RUN mkdir benchmarks
RUN mkdir results

# Copy executable file
ADD run-confuzzius.sh /root/

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]
