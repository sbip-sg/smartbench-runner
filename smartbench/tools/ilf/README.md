# Tool ILF

# Installation

## Using Docker

## Manual installation

- Run `install-ilf-manual.sh` to install Go-Ethereum and ILF.

- Check ILF's `README.md` to install other utilites.

# Usage

## Notes

- Before fuzzing any smart contract, check if `Solc` compiler is switched to the
  correct version specified by the input smart contract.

## Fuzzing new contract

- Remember to configure the correct `GOPATH` used by ILF.

- Put the new contract into `ilf/example/project/contracts`.

- Update the contract name to the deployment script
  `example/project/migrations/2_deploy_contracts.js`.

- Run the script to extract deployment transactions of the contracts:

  ```sh
  GOPATH=/path/to/ILF/go/path/ python3 script/extract.py --proj example/project/ --port 8545
  ```

- Run ILF to fuzz the new contract:

  ```sh
  python3 -m ilf --proj ./example/project/ --contract <ContractName> \
          --fuzzer imitation --model ./model/ --limit 2000
  ```


## Running using Docker:

  ```sh
  cd smartbench/tools/ilf/repo/ilf/
  docker run -it ilf
  ```

## Running manually
