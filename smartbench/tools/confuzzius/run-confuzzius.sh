#!/bin/bash

# Usage:
#   ./run-confuzzius.sh -f <test-file> [confuzzius-arguments]
#

################################################
# Print usage and help

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-confuzzius.sh -f <test-file> -c <contract-name> -o <output-dir> -t <timeout> --solc-version <version> [confuzzius-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>            Smart contract file to be analyzed."
    echo "  -c <contract-name>        Name of the target contract."
    echo "  -o <output-dir>           Output directory."
    echo "  -t <timeout>              Timeout for each target contract."
    echo "  --solc-version <version>  Solidity version to be used, auto detect if omitted."
    echo "  -h, --help                Print this usage."
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
CONTRACT_NAME=""
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
            CONTRACT_NAME=$2
            shift  # past argument
            shift  # past value
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
    SOLC_VER=$(solc-detect -q $TEST_FILE)
fi

COMPILED_CONTRACTS_DIR="$OUTPUT_DIR/compiled_contracts"
rm -rf $COMPILED_CONTRACTS_DIR
mkdir $COMPILED_CONTRACTS_DIR

SOLC_VERSION=$SOLC_VER solc $TEST_FILE --bin --abi \
    -o $COMPILED_CONTRACTS_DIR --overwrite \
    1>/dev/null 2>&1  # Do not capture output of Solc

################################################
# Analyze contracts

if [ $CONTRACT_NAME == ""]
then
    SOLC_VERSION=$SOLC_VER python "$TOOL_DIR/fuzzer/main.py" --evm byzantium \
        -s $TEST_FILE -t $TIMEOUT \
        -r "$OUTPUT_DIR/$CONTRACT/confuzzius_result.json" \
        ${ADDITIONAL_ARGS[@]} 2>&1
else
    SOLC_VERSION=$SOLC_VER python "$TOOL_DIR/fuzzer/main.py" --evm byzantium \
        -s $TEST_FILE  -c $CONTRACT_NAME -t $TIMEOUT \
        -r "$OUTPUT_DIR/$CONTRACT/confuzzius_result.json" \
        ${ADDITIONAL_ARGS[@]} 2>&1
fi
