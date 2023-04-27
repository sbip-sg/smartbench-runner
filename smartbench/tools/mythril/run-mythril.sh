#!/bin/bash

# Usage:
#   ./run-mythril.sh -f <test-file> [mythril-arguments]
#

################################################
# Print usage and help

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-mythril.sh -f <test-file> -c <contract-name> -o <output-dir> -t <timeout> --solc-version <version> [confuzzius-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>            Smart contract file to be analyzed."
    echo "  -o <output-file>          Output directory."
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
        -o)
            OUTPUT_FILE=$2
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

# Checking test file
if [[ $OUTPUT_FILE == "" ]]; then
    echo "Error: output file is not specified!"
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
# Analyze contracts

myth analyze $TEST_FILE --solv $SOLC_VER --execution-timeout $TIMEOUT -o json > $OUTPUT_FILE
