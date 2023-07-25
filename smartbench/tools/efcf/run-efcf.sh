#!/usr/bin/bash

# Usage:
#   ./run-efcf.sh -f <test-file> [efcf-arguments]
#

################################################
# Print usage and help

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-efcf.sh -f <test-file> [efcf-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>            Smart contract file to be analyzed."
    echo "  -o <output-file>          Output JSON file."
    echo "  -t <timeout>              Timeout for each target contract."
    echo "  --solc-version <version>  Solidity version to be used, auto detect if omitted."
    echo "  -h, --help                Print this usage."
    echo ""
    echo "Addtional arguments passing to Efcf can be put at the end of this command."
}

print_help () {
    echo ""
    echo "Please run with '-h' to see the command usage."
}

################################################
# Parse arguments

TEST_FILE=""
OUTPUT_JSON_FILE=""
TIMEOUT=0
ADDITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -f)
            TEST_FILE=$(realpath $2)
            shift # past argument
            shift # past value
            ;;
        -o)
            OUTPUT_JSON_FILE="$2"
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
    echo "Error: output dir is not specified!"
    print_help
    exit 1
fi

# Checking Solc version
if [[ $SOLC_VER == "" ]]; then
    echo "Error: Solc version is not specified!"
    print_help
    exit 1
fi

################################################
# Analyze test file

# Run Efcf
efcfuzz --solc-version $SOLC_VER --source  $TEST_FILE --out $OUTPUT_JSON_FILE \
        --timeout $TIMEOUT ${ADDITIONAL_ARGS[@]} --report-leaking-ether \
        --report-dos-selfdestruct 2>&1
