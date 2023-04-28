# Smartbench Runner


# Installation

## Install each components

- Download source code and benchmarks

  + Download source code for the first time:

    ```sh
    git clone https://github.com/sbip-sg/smartbench-runner
    cd smartbench-runner

    # Update benchmarking and result folders (`benchmarks` and `results`)
    git submodule update --init --recursive
    ```

  + Pull the newest source code of both the main repository and submodules:

    ``` sh
    git pull --recurse-submodules
    ```

- Install Python virtual environment and required packages:

  ```sh
  cd smartbench-runner
  ./scripts/install-smartbench-env.sh
  ```

- Install Docker containers for analysis tools:

  ```sh
  # Install 30 docker containers for all tools
  ./scripts/install-tool-docker.sh -t all -n 30 --use-remote-images --force-install

  # Install 5 docker containers named: slither-1, ..., slither-5
  ./scripts/install-tool-docker.sh -t slither -n 5 --use-remote-images --force-install
  ```

## Install and update everything

- Run the following scripts

  ```sh
  git clone https://github.com/sbip-sg/smartbench-runner
  cd smartbench-runner

  # Update source code and its sub modules
  ./scripts/update-all-source-code.sh

  # Install Smartbench environment and Docker containers for all tools
  ./scripts/install-everything.sh
  ```

# Usage

## Features

### Analysis

- Benchmarking folder structure:
  + Test files must be copied to: `smartbench-runner/benchmarks`.
  + The result will be recorded to `smartbench-runner/results`.

- Sample command to run `confuzzius` against the `access_control` category of `Smartbugs`:

  ```sh
  ./smartbench.sh analyze -t confuzzius --jobs 5 --timeout 10 \
                  -f benchmarks/smartbench-dataset/solidity/smartbugs++/access_control
  ```

- Run with `--solc-version` to specify a specific version of the Solc compiler.

- Run with `--install-smartbench-env --install-remote-docker` to update the
  newest Smartbench and Docker environment

- Run with `--validate` and `--benchmarking` to verify the output analysis result.

### Parse result

- `parse-results`: parse existing raw results obtained from previous analyses.

  ```sh
  ./smartbench.sh parse-results results/<path_to_results>/
  ```

### Parse bug annotations

- `parse-annots`: parse bug annotations in smart contracts.

  ```sh
  ./smartbench.sh parse-annots examples/**.sol
  ```

# Development

- Code formatting is performed by `black` (see `format-code.sh`).
