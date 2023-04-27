#!/bin/bash

# Usage:
#   ./run-ilf.sh -f <test-file> -c <contract-names> [options] [ilf-arguments]
#

################################################
# Print usage and help

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-ilf.sh -f <test-file> -c <contract-names> [options] [ilf-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>            Smart contract file to be analyzed."
    echo "  -c <contract-names>       Names of contracts to be analyzed (whitespace separated)."
    echo "  -o <output-dir>           Output directory containing analysis results."
    echo "  -t <timeout>              Timeout for each contract of the test file."
    echo "  --solc-version <version>  Solidity version to be used, auto detect if omitted."
    echo "  -h, --help                Print this usage."
    echo ""
    echo "Addtional arguments passing to ILF can be put at the end of this command."
}

print_help () {
    echo ""
    echo "Please run with '-h' to see the command usage."
}

################################################
# Parse arguments

TEST_FILE=""
CONTRACT_NAMES=()
TIMEOUT=0
OUTPUT_DIR=""
ADDITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -f)
            TEST_FILE=$(realpath $2)
            shift # past argument
            shift # past value
            ;;
        -c)
            shift # past argument
            # Parse contract names
            while [[ $# -gt 0 ]]; do
                case $1 in
                    -*|--*)
                        break
                        ;;
                    *)
                        CONTRACT_NAMES+=("$1")
                        shift  # past value
                        ;;
                esac
            done
            ;;
        -o)
            OUTPUT_DIR="$2"
            shift  # past argument
            shift  # past value
            ;;
        -t)
            TIMEOUT=$2
            shift  # past argument
            shift  # past value
            ;;
        --solc-version)
            SOLC_VER=$2
            shift  # past argument
            shift  # past value
            ;;
        -h|--help)
            print_usage
            exit 1
            ;;
        *)
            ADDITIONAL_ARGS+=("$1") # save all other arguments
            shift # past argument
            ;;
    esac
done

# Checking test file
if [[ $TEST_FILE == "" ]]; then
    echo "Error: test file is not specified!"
    print_help
    exit 1
fi

# Checking Solc version
if [[ $SOLC_VER == "" ]]; then
    echo "Error: Solc version is not specified!"
    print_help
    exit 1
fi

# Checking output dir
if [[ $OUTPUT_DIR == "" ]]; then
    echo "Error: output dir is not specified!"
    print_help
    exit 1
fi

# Checking timeout
if [[ $TIMEOUT -lt 0 ]]; then
    echo "Error: timeout is invalid or not specified!"
    print_help
    exit 1
fi

################################################
# Configure paths

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    GO_DIR="/root/go"
    TEMPLATE_DIR="/root/template"
else
    BASE_DIR="$(realpath $(dirname "$0"))"
    GO_DIR="$BASE_DIR/repo/go"
    TEMPLATE_DIR="$BASE_DIR/template"
fi
TOOL_DIR="$GO_DIR/src/ilf"

################################################
# Deploy contracts using Truffle as required by ILF

echo "Make truffle project for testing file"

# Create a fresh truffle-based project to deploy test contracts
mkdir -p $OUTPUT_DIR
OUTPUT_DIR="$(realpath $OUTPUT_DIR)"
PROJECT_DIR="$OUTPUT_DIR/truffle-project"
rm -rf $PROJECT_DIR
mkdir -p $PROJECT_DIR
mkdir -p "$PROJECT_DIR/contracts" "$PROJECT_DIR/build/contracts"
mkdir -p "$PROJECT_DIR/migrations" "$PROJECT_DIR/test"

# Copy test file containing target contracts
cp $TEST_FILE "$PROJECT_DIR/contracts/"

# Create truffle configuration file
CONFIG_FILE="$PROJECT_DIR/truffle-config.js"
cat > $CONFIG_FILE <<EOF
module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*",
      gas: 1000000000
    }
  },
  compilers: {
    solc: {
      version: "native",
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  }
};
EOF

# Create deployment file for input contract
DEPLOY_FILE="$PROJECT_DIR/migrations/2_deploy_contracts.js"
rm -rf $DEPLOY_FILE
touch $DEPLOY_FILE
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "var contract$CONTRACT = artifacts.require(\"$CONTRACT\");" >> $DEPLOY_FILE
done
echo "" >> $DEPLOY_FILE
echo "module.exports = function(deployer) {" >> $DEPLOY_FILE
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "  deployer.deploy(contract$CONTRACT);"  >> $DEPLOY_FILE
done
echo "};" >> $DEPLOY_FILE

# Deploy contracts and extract deployment transactions
SOLC_VERSION=$SOLC_VER GOPATH=$GO_DIR \
    python3 "$TOOL_DIR/script/extract.py" --proj $PROJECT_DIR --port 8545

################################################
# Analyze contracts

# Fuzz each contract using the pre-trained model of ILF
cd $TOOL_DIR
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo ""
    echo "==============================="
    echo ""
    echo "Fuzzing contract: $CONTRACT"
    echo ""
    GOPATH=$GO_DIR python3 -m ilf --proj $PROJECT_DIR --contract $CONTRACT \
        --timeout $TIMEOUT --limit 2000 --fuzzer imitation --model ./model/
done
