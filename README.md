# Smartbench Runner


# Installation

- Download source code and benchmarks:

  ```sh
  git clone https://github.com/sbip-sg/smartbench-runner
  cd smartbench-runner

  # Update benchmarking and result folders (`benchmarks` and `results`)
  git submodule update --init --recursive
  ```

- Install Python virtual environment and required packages:

  ```sh
  cd smartbench-runner
  ./install-smartbench-env.sh
  ```

- Install Docker locally (optional):

  ```sh
  # Install 5 docker containers named: slither-1, ..., slither-5
  ./install-tool-docker.sh -t slither --force-install -n 5
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
