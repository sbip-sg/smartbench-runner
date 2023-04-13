#!/bin/bash

# Usage:
#   ./run-smartian.sh -f <test-file> -c <contract-names> [options] [smartian-arguments]
#

################################################
# Usage

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-smartian.sh <test-file> -c <contract-names> [options] [smartial-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>        Smart contract file to be analyzed."
    echo "  -c <contract-names>   Names of contracts to be analyzed (whitespace separated)."
    echo "  -o <output-dir>       Output directory containing analysis results."
    echo "  -t <timeout>          Timeout for each contract of the test file."
    echo "  -h, --help            Print this usage."
    echo ""
    echo "Addtional arguments passing to Smartian can be put at the end of this command."
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

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    TOOL_DIR="/root/smartian"
else
    TOOL_DIR="$(realpath $(dirname "$0"))/repo/smartian"
fi

################################################
# Compile contracts

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

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

# Run Smartian on each candidate contract
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "==============================="
    echo "** Fuzzing contract: $CONTRACT"
    dotnet $TOOL_DIR/build/Smartian.dll fuzz \
        --useothersoracle --checkoptionalbugs --verbose 1 \
        --program "$COMPILED_CONTRACTS_DIR/$CONTRACT.bin" \
        --abifile "$COMPILED_CONTRACTS_DIR/$CONTRACT.abi" \
        --outputdir $OUTPUT_DIR --timelimit $TIMEOUT \
        ${ADDITIONAL_ARGS[@]} 2>&1
done
