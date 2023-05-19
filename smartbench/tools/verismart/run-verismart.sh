#!/bin/bash

# Usage:
#   ./run-verismart.sh -f <test-file> -c <contract-names> [options] [verismart-arguments]
#

################################################
# Usage

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-verismart.sh -f <test-file> -c <contract-names> [options] [smartial-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>            Smart contract file to be analyzed."
    echo "  -c <contract-names>       Names of target contracts (whitespace separated)."
    echo "  -o <output-dir>           Output directory containing analysis results."
    echo "  -t <timeout>              Timeout for each target contract."
    echo "  --solc-version <version>  Solidity version to be used, auto detect if omitted."
    echo "  -h, --help                Print this usage."
    echo ""
    echo "Addtional arguments passing to VeriSmart can be put at the end of this command."
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
    echo "Error: test file is not specified!"
    print_help
    exit 1
fi

# Checking Solc version
if [[ $SOLC_VER == "" ]]; then
    echo "Error: Solc version is not specified!"
    print_help
    exit 1
fi

# Checking output dir
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

TOOL_DIR="/root/verismart"

################################################
# Analyze contracts

# Run VeriSmart on each candidate contract
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo ""
    echo "==============================================================="
    echo "Fuzzing contract: $CONTRACT"
    echo ""
    SOLC_VERSION=$SOLC_VER $TOOL_DIR/main.native \
        -input $TEST_FILE -main $CONTRACT \
        -outdir $OUTPUT_DIR -verify_timeout $TIMEOUT \
        ${ADDITIONAL_ARGS[@]} 2>&1
done
