# Slither

# Installation

## Docker

- Build a local Docker:

  ```sh
  cd smartbench/tools/slither
  docker build -t slither .
  ```

# Usage

- Run Slither with Solc version specified by the flag `--solc-solcs-select`:

  ```sh
  slither BecToken.sol --solc-solcs-select 0.4.25
  ```

- Run Slither with Solc version specified by the environment variable
  `SOLC_VERSION` of `solc-select`:

  ```sh
  SOLC_VERSION=0.4.25 slither BecToken.sol
  ```
