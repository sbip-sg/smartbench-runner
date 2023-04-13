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
ADDITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -f)
            TEST_FILE=$(realpath $2)
            shift # past argument
            shift # past value
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
    echo "Error: output dir is not specified!"
    print_help
    exit 1
fi

################################################
# Analyze test file

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    TOOL_DIR="/root/confuzzius"
else
    TOOL_DIR="$(realpath $(dirname "$0"))/repo/confuzzius"
fi

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# set the solc version
solc-select use $SOLC_VER

# Run Confuzzius
python "$TOOL_DIR/fuzzer/main.py" --evm byzantium \
    -s $TEST_FILE ${ADDITIONAL_ARGS[@]} 2>&1
