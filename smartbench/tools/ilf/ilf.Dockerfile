# Dockerfile for ILF

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

# Install some libraries
RUN apt -y install libssl-dev curl pkg-config

# Install Nodejs truffle web3 ganache-cli
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get -y install nodejs
RUN npm -g config set user root
RUN npm install -g truffle web3 ganache-cli

# Install Golang and prepare workspace
WORKDIR /root/
RUN wget https://dl.google.com/go/go1.10.4.linux-amd64.tar.gz
RUN tar -xvf go1.10.4.linux-amd64.tar.gz
RUN mv go /usr/lib/go-1.10
RUN mkdir go
ENV GOPATH=/root/go
ENV GOROOT=/usr/lib/go-1.10
ENV PATH=$GOPATH/bin:$GOROOT/bin:$PATH

# Install z3
WORKDIR /root/
RUN git clone https://github.com/Z3Prover/z3.git
WORKDIR /root/z3
RUN git checkout z3-4.8.6
RUN python3 scripts/mk_make.py --python
WORKDIR /root/z3/build
RUN make -j7
RUN make install

# Clone ILF
WORKDIR $GOPATH/src/
RUN git clone https://github.com/taquangtrung/ilf ilf

# Install Go-Ethereum and apply ILF patch
RUN mkdir -p $GOPATH/src/github.com/ethereum/
WORKDIR $GOPATH/src/github.com/ethereum/
RUN git clone https://github.com/ethereum/go-ethereum.git
WORKDIR $GOPATH/src/github.com/ethereum/go-ethereum
RUN git checkout 86be91b3e2dff5df28ee53c59df1ecfe9f97e007
RUN git apply $GOPATH/src/ilf/script/patch.geth

# Install ILF's dependencies
WORKDIR $GOPATH/src/ilf
RUN pip install cython
RUN pip install -r requirements-aiohttp.txt --no-cache-dir
RUN pip install aiohttp
RUN pip install numpy
RUN pip install scipy>=0.17.0
RUN pip install -r requirements.txt
RUN pip install torch==1.10.2+cpu torchvision==0.11.3+cpu torchaudio==0.10.2+cpu\
    -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Compile ILF
RUN go build -o execution.so -buildmode=c-shared export/execution.go

# Copy executable file
ADD smartbench/tools/ilf/run-ilf.sh /root/

# Entry point when running the container as an executable
ENTRYPOINT [ "/bin/bash" ]
