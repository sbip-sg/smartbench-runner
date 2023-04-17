#!/usr/bin/bash

# Usage:
#   ./run-slither.sh -f <test-file> [slither-arguments]
#

################################################
# Print usage and help

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-slither.sh -f <test-file> [slither-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>        Smart contract file to be analyzed."
    echo "  -h, --help            Print this usage."
    echo ""
    echo "Addtional arguments passing to Slither can be put at the end of this command."
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

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Run Slither
SOLC_VERSION=$SOLC_VER slither $TEST_FILE ${ADDITIONAL_ARGS[@]} 2>&1
