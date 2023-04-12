#!/bin/bash

# Usage:
#   ./run-ilf.sh -f <test-file> [-c <contract names>] [additional-ilf-arguments]
#
# NOTE:
#   - Test file must be the first argument
#   - Contract names are whitespace-separated
#   - This script must be configured so that it can be used both to run
#     in a Docker container as well as to run locally.
#

################################################
# Usage

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-ilf.sh -f <test-file> [options] [additional-smartial-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>        Smart contract file to be analyzed."
    echo "  -c <contract-names>   Names of contracts to be analyzed (whitespace separated)."
    echo "  -o <output-dir>       Output directory containing analysis results."
    echo "  -t <timeout>          Timeout for each contract of the test file."
    echo "  -h, --help            Print this usage."
    echo ""
    echo "Note: arguments not matching the above list will be passed directy to ILF."
}

print_run_help () {
    echo ""
    echo "Please run this command again with '-h' to see help messages!"
}

################################################
# Parse arguments

TEST_FILE=""
CONTRACT_NAMES=()
TIMEOUT=0
OUTPUT_DIR=""
RESULT_FILE=""
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

# Checking output dir
if [[ $OUTPUT_DIR == "" ]]; then
    echo "Error: output dir is not specified!"
    print_run_help
    exit 1
fi

# Checking timeout
if [[ $TIMEOUT -lt 0 ]]; then
    echo "Error: timeout is not specified or invalid!"
    print_run_help
    exit 1
fi

################################################
# Configure paths

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    GO_DIR="/root/go"
    TEMPLATE_DIR="/root/template"
else
    BASE_DIR="$(realpath $(dirname "$0"))"
    GO_DIR="$BASE_DIR/repo/go"
    TEMPLATE_DIR="$BASE_DIR/template"
fi
TOOL_DIR="$GO_DIR/src/ilf"

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

################################################
# Deploy contracts using Truffle as required by ILF

echo "Make truffle project for testing file"

# Copy truffle-based template project
mkdir -p $OUTPUT_DIR
OUTPUT_DIR="$(realpath $OUTPUT_DIR)"
PROJECT_DIR="$OUTPUT_DIR/truffle-project"
cp -r "$TEMPLATE_DIR/truffle-project" $PROJECT_DIR

# Copy test file
cp $TEST_FILE "$PROJECT_DIR/contracts/"

# Create deployment file for input contracts
DEPLOY_FILE="$PROJECT_DIR/migrations/2_deploy_contracts.js"
rm -rf $DEPLOY_FILE
touch $DEPLOY_FILE
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "var contract$CONTRACT = artifacts.require(\"$CONTRACT\");" >> $DEPLOY_FILE
done
echo "" >> $DEPLOY_FILE
echo "module.exports = function(deployer) {" >> $DEPLOY_FILE
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "  deployer.deploy(contract$CONTRACT);"  >> $DEPLOY_FILE
done
echo "};" >> $DEPLOY_FILE

# Extract deployment transactions
GOPATH=$GO_DIR python3 "$TOOL_DIR/script/extract.py" --proj $PROJECT_DIR --port 8545

################################################
# Analyze contracts

# Run ILF to fuzz each contract using pre-trained model
cd $TOOL_DIR
for CONTRACT in ${CONTRACT_NAMES[@]}; do
    echo "==============================="
    echo "** Fuzzing contract: $CONTRACT"
    GOPATH=$GO_DIR python3 -m ilf --proj $PROJECT_DIR --contract $CONTRACT \
        --limit 2000 --fuzzer imitation --model ./model/
done
