# Smartbench Runner

# Installation

- Install Python virtual environment and required packages:

  ```sh
  cd smartbench-runner
  ./install.sh
  ```

# Usage

## Analiss mode

- Run `analyze` sub-command for new analyses.

  ```sh
  # Input a single file
  ./smartbench.sh analyze examples/Rubixi.sol -t slither

  # Input a wild-card pattern
  ./smartbench.sh analyze examples/*.sol -t slither

  # Input a directory
  ./smartbench.sh analyze examples -t slither
  ```

- Run with `--validate-results` to validate all detected issues.

  ```sh
  # Validate analysis results
  ./smartbench.sh analyze examples -t slither --validate-results
  ```

## Parsing results

- Run `parse-results` sub-command to read existing results.

  ```sh
  ./smartbench.sh parse-results results/<path_to_results>/
  ```

- Run with `--validate-results` to validate all detected issues.

  ```sh
  ./smartbench.sh parse-results results/<path_to_results>/ --validate-results
  ```

## Parsing bug annotations

- Run `parse-annots` sub-command to collect bug annotations in smart contracts.

  ```sh
  # Input a single file
  ./smartbench.sh parse-annots examples/Rubixi.sol

  # Input a wild-card pattern
  ./smartbench.sh parse-annots examples/*.sol

  # Input a directory
  ./smartbench.sh parse-annots examples
  ```

# Development

- Code formatting is performed by `black` (see configuration in `pyproject.toml`).
