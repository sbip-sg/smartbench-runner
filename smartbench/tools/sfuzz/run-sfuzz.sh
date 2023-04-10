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
OUTPUT_DIR=""
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
        *)
            ADDITIONAL_ARGS+=("$1") # save all other arguments
            shift # past argument
            ;;
    esac
done

# Checking output dir
if [[ $OUTPUT_DIR == "" ]]; then
    echo "sFuzz: output dir is not specified!"
    exit 1
fi

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

# Compile test file to contracts in ABI and BIN format
CONTRACTS_DIR="$OUTPUT_DIR/compiled_contracts"
rm -rf $CONTRACTS_DIR
mkdir $CONTRACTS_DIR
SOLC_VERSION=$SOLC_VER solc $TEST_FILE --bin --abi \
    -o $CONTRACTS_DIR --overwrite \
    1>/dev/null 2>&1  # Do not capture output of Solc

if [[ ${#CONTRACT_NAMES[@]}  == 0 ]]; then
    CURRENT_DIR=$(pwd)
    cd $CONTRACTS_DIR
    CONTRACT_NAMES=($(ls -1 *.bin | sed "s/\.bin//"))
    cd $CURRENT_DIR
fi

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

./fuzzer -g \
         -r 0 \
         -d $TIMEOUT \
         --attacker ReentrancyAttacker 2>&1
chmod +x fuzzMe
./fuzzMe

