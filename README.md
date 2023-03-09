# Smartbench Runner

# Installation

- Install Python virtual environment:

  ```sh
  cd smartbench-runner
  ./install/setup-venv.sh
  ```

# Usage

- Run `analyze` sub-command:

  ```sh
  # Input a single file
  ./smartbench.sh analyze examples/Rubixi.sol -t slither

  # Input a wild-card pattern
  ./smartbench.sh analyze examples/*.sol -t slither

  # Input a directory
  ./smartbench.sh analyze examples -t slither
  ```

# Development

- Code formatting is performed by `black` (see configuration in `pyproject.toml`).
