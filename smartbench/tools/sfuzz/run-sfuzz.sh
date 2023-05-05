#!/bin/bash

# Usage:
#   ./run-sfuzz.sh -f <test-file> [options] [sfuzz-arguments]
#

################################################
# Print usage and help

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-sfuzz.sh -f <test-file> -c <contract-name> -o <output-dir> -t <timeout> --solc-version <version> [sfuzz-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>            Smart contract file to be analyzed."
    echo "  -c <contract-name>        Name of the target contract."
    echo "  -o <output-dir>           Output directory."
    echo "  -t <timeout>              Timeout for each target contract."
    echo "  --solc-version <version>  Solidity version to be used, auto detect if omitted."
    echo "  -h, --help                Print this usage."
    echo ""
    echo "Addtional arguments passing to sFuzz can be put at the end of this command."
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
SOLC_VER=""
ADDITIONAL_ARGS=()

# Parse arguments
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
        *)
            ADDITIONAL_ARGS+=("$1") # save all other arguments
            shift # past argument
            ;;
    esac
done

# Checking test file
if [[ $TEST_FILE == "" ]]; then
    echo "Error: input file is not specified!"
    print_help
    exit 1
fi

# Checking Solc version
if [[ $SOLC_VER == "" ]]; then
    echo "Error: Solc version is not specified!"
    print_help
    exit 1
fi

# Checking timeout
if [[ $TIMEOUT -lt 0 ]]; then
    echo "sFuzz: timeout is not specified or invalid!"
    exit 1
fi

################################################
# Configure paths

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    TOOL_DIR="/root/sfuzz"
else
    TOOL_DIR="$(realpath $(dirname "$0"))/repo/sfuzz"
fi

# Run sFuzz insider the `build/fuzzer` repository
cd $TOOL_DIR/build/fuzzer
rm -rf contracts
mkdir contracts
rm -rf output
mkdir output

# Run sFuzz on each candidate contract
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "==============================="
    echo ""
    echo "Fuzzing contract: $CONTRACT"
    echo ""
    cp $TEST_FILE "contracts/$CONTRACT.sol"
done

SOLC_VERSION=$SOLC_VER ./fuzzer -g -r 0 -d $TIMEOUT --attacker ReentrancyAttacker 2>&1
chmod +x fuzzMe
SOLC_VERSION=$SOLC_VER ./fuzzMe
