# Dockerfile for VeriSmart

# Usage: this file should only be run by the installation script:
# `smartbench-runner/install-tool-docker.sh`

# Use the base image of Smartbench
FROM smartbench/base:latest

# Install Ubuntu and OCaml dependencies
WORKDIR /root/
RUN apt update
RUN apt install -y opam libgmp-dev
RUN opam init --auto-setup --yes --bare --disable-sandboxing \
    && opam switch create system ocaml-system
RUN eval $(opam env) && \
    opam install -y conf-m4.1 ocamlfind ocamlbuild num yojson batteries ocamlgraph zarith

# Install Z3
WORKDIR /root/
RUN git clone https://github.com/Z3Prover/z3.git
WORKDIR /root/z3
RUN git checkout z3-4.8.9
RUN eval $(opam env) && python3 scripts/mk_make.py --ml
WORKDIR /root/z3/build
RUN eval $(opam env) && make -j7
RUN eval $(opam env) && make install

# Install VeriSmart
WORKDIR /root/
RUN git clone https://github.com/kupl/VeriSmart-public verismart
WORKDIR /root/verismart
RUN chmod +x build
RUN eval $(opam env) && ./build

# Entry point when running the container as an executable
WORKDIR /root/
ENTRYPOINT [ "/bin/bash" ]
