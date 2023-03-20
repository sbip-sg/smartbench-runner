# Tool Smartian

# Installation

## Using Docker

## Manual installation

- Install [Dotnet 5 SDK] (https://www.davidhayden.me/blog/install-net5-on-ubuntu-20-04):

  ```sh
  wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb \
       -O packages-microsoft-prod.deb
  sudo dpkg -i packages-microsoft-prod.deb

  sudo apt-get update
  sudo apt-get install -y apt-transport-https &&
  sudo apt-get update 
  sudo apt-get install -y dotnet-sdk-5.0
  ```

- Install Smartian like as specified in README:

  ```sh
  git clone https://github.com/SoftSec-KAIST/Smartian
  cd Smartian
  git submodule update --init --recursive
  make
  ```

# Usage
