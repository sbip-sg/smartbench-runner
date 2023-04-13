#!/bin/bash

# Usage:
#   ./run-mythril.sh <test-file> -t timeout
#
# NOTE:
#   - Test file must be the first argument
#   - Contract names are whitespace-separated
#   - This script must be configured so that it can be used both to run
#     in a Docker container as well as to run locally.
#

# Arguments of mythril
TEST_FILE=$(realpath $1)
shift  # Past test file

TIMEOUT=0
RESULT_FILE=""
OUTPUT_FILE=""
ADDITIONAL_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t)
            TIMEOUT=$2
            shift  # past argument
            shift  # past value
            ;;
        -o)
            OUTPUT_FILE=$2
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
    echo "mythril: timeout is not specified or invalid!"
    exit 1
fi

# Checking output dir
if [[ $OUTPUT_FILE == "" ]]; then
    echo "Error: output file is not specified!"
    exit 1
fi


# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

myth analyze $TEST_FILE --solv $SOLC_VER --execution-timeout $TIMEOUT -o json > $OUTPUT_FILE
