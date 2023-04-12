#!/bin/bash

# Usage:
#   ./run-sfuzz.sh <test-file> [-c <contract names>] [additional-sfuzz-arguments]
#
# NOTE:
#   - Test file must be the first argument
#   - Contract names are whitespace-separated
#   - This script must be configured so that it can be used both to run
#     in a Docker container as well as to run locally.
#

# Arguments of sFuzz
TEST_FILE=$(realpath $1)
shift  # Past test file

CONTRACT_NAMES=()
TIMEOUT=0
RESULT_FILE=""
ADDITIONAL_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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
        *)
            ADDITIONAL_ARGS+=("$1") # save all other arguments
            shift # past argument
            ;;
    esac
done

# Checking timeout
if [[ $TIMEOUT -lt 0 ]]; then
    echo "sFuzz: timeout is not specified or invalid!"
    exit 1
fi

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    TOOL_ROOT_PATH="/root/sfuzz"
else
    TOOL_ROOT_PATH="$(realpath $(dirname "$0"))/repo/sfuzz"
fi

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Run sFuzz insider the `build/fuzzer` repository
cd $TOOL_ROOT_PATH/build/fuzzer
rm -rf contracts
mkdir contracts
rm -rf output
mkdir output

# Run sFuzz on each candidate contract
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "==============================="
    echo "** Fuzzing contract: $CONTRACT"
    cp $TEST_FILE "contracts/$CONTRACT.sol"
done

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

solc-select use $SOLC_VER

./fuzzer -g -r 0 -d $TIMEOUT --attacker ReentrancyAttacker 2>&1
chmod +x fuzzMe
./fuzzMe

