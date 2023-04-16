# Smartbench Runner

# Installation

- Install Python virtual environment and required packages:

  ```sh
  cd smartbench-runner
  ./install-smartbench-env.sh
  ```

- Install Docker containers for each analysis tool:

  ```sh
  # Install 5 docker containers named: slither-1, ..., slither-5
  ./install-tool-docker.sh -t slither --force-install -n 5
  ```

# Usage

## Features

- `analyze`: analyze contracts and record results

  ```sh
  ./smartbench.sh analyze examples -t slither
  ./smartbench.sh analyze examples/*.sol -t slither
  ```

- `parse-results`: parse existing raw results obtained from previous analyses.

  ```sh
  ./smartbench.sh parse-results results/<path_to_results>/
  ```

- `parse-annots`: parse bug annotations in smart contracts.

  ```sh
  ./smartbench.sh parse-annots examples/**.sol
  ```

## Benchmarking mode

- Benchmarking structure:
  + Test files must be copied to: `smartbench-runner/benchmarks`.
  + The result will be recorded to `smartbench-runner/results`.

- Sample commands:

  ```sh
  # Benchmarking smartbugs dataset using 3 docker jobs, timeout 60s per test file
  ./smartbench.sh benchmarks/smartbugs -t confuzzius --docker --jobs 3 --timeout 10
  ```

# Development

- Code formatting is performed by `black` (see `format-code.sh`).
