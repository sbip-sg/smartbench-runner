# Tool ILF

# Installation

## Using Docker

## Manual installation

- Run `install-ilf-manual.sh` to install Go-Ethereum and ILF.

- Check ILF's `README.md` to install other utilites.

# Usage

- Before fuzzing any smart contract, check if `Solc` compiler is switched to the
  correct version specified by the input smart contract.

- Running using Docker:

  ```sh
  cd smartbench/tools/ilf/repo/ilf/
  docker run -it ilf
  ```
