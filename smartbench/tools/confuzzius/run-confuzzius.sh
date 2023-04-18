#!/bin/bash

# Usage:
#   ./run-confuzzius.sh -f <test-file> [confuzzius-arguments]
#

################################################
# Print usage and help

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-confuzzius.sh -f <test-file> [confuzzius-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>        Smart contract file to be analyzed."
    echo "  -c <contract-names>   Names of target contracts (whitespace separated)."
    echo "  -o <output-dir>       Output directory."
    echo "  -t <timeout>          Timeout for each target contract."
    echo "  --solc-version <version>  Solidity version to be used, auto detect if omitted."
    echo "  -h, --help            Print this usage."
    echo ""
    echo "Addtional arguments passing to Confuzzius can be put at the end of this command."
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
SOLC_VER=""
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
    echo "Error: input file is not specified!"
    print_help
    exit 1
fi

# Checking test file
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
    TOOL_DIR="/root/confuzzius"
else
    TOOL_DIR="$(realpath $(dirname "$0"))/repo/confuzzius"
fi

################################################
# Compile contracts

# Auto-detect Solc version if it wasn't specified
if [[ $SOLC_VER == "" ]]; then
    SOLC_VER=$(solc-detect $TEST_FILE)
fi

COMPILED_CONTRACTS_DIR="$OUTPUT_DIR/compiled_contracts"
rm -rf $COMPILED_CONTRACTS_DIR
mkdir $COMPILED_CONTRACTS_DIR

SOLC_VERSION=$SOLC_VER solc $TEST_FILE --bin --abi \
    -o $COMPILED_CONTRACTS_DIR --overwrite \
    1>/dev/null 2>&1  # Do not capture output of Solc

# If contract names are not specified from the input, analyze all contracts
# obtained after compilation.
if [[ ${#CONTRACT_NAMES[@]}  == 0 ]]; then
    CURRENT_DIR=$(pwd)
    cd $COMPILED_CONTRACTS_DIR
    CONTRACT_NAMES=($(ls -1 *.bin | sed "s/\.bin//"))
    cd $CURRENT_DIR
fi

################################################
# Analyze contracts

# Run Confuzzius on each candidate contract
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "==============================="
    echo "** Fuzzing contract: $CONTRACT"
    echo "** OUTPUT: $OUTPUT_DIR/$CONTRACT/confuzzius_result.json"
    mkdir -p "$OUTPUT_DIR/$CONTRACT"
    SOLC_VERSION=$SOLC_VER python "$TOOL_DIR/fuzzer/main.py" --evm byzantium \
        -s $TEST_FILE -c $CONTRACT -t $TIMEOUT \
        -r "$OUTPUT_DIR/$CONTRACT/confuzzius_result.json" \
        ${ADDITIONAL_ARGS[@]} 2>&1
done
