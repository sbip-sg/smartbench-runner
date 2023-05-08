#!/bin/bash

# Usage:
#   ./run-smartfuzz.sh -f <test-file> [options] [smartfuzz-arguments]
#

################################################
# Usage

print_usage () {
    echo ""
    echo "Usage: "
    echo "  run-smartian.sh -f <test-file> -c <contract-names> [options] [smartial-arguments]"
    echo ""
    echo "Options:"
    echo "  -f <test-file>               Smart contract file to be analyzed."
    echo "  -r <result-file>             Output file containing analysis result."
    echo "  -c <contract-name>        Name of the target contract."
    echo "  --coverage <coverage-file>   Output file containing code coverage."
    echo "  -t <timeout>                 Timeout for each target contract."
    echo "  --time-distribution <value>  Default or equal time distribution for each contract."
    echo "  -h, --help                   Print this usage."
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
RESULT_FILE=""
COVERAGE_FILE=""
TIMEOUT=0
RANDOM_SEED=0
TIME_DISTRIBUTION=""
TIME_DISTRIBUTION_ARGS=""
CONTRACT_ARGS=""
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
        -r)
            RESULT_FILE="$2"
            shift  # past argument
            shift  # past value
            ;;
        --coverage)
            COVERAGE_FILE="$2"
            shift  # past argument
            shift  # past value
            ;;
        -t)
            TIMEOUT=$2
            shift  # past argument
            shift  # past value
            ;;
        --time-distribution)
            TIME_DISTRIBUTION=$2
            shift  # past argument
            shift  # past value
            ;;
        --random-seed)
            RANDOM_SEED=$2
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

if [[ $TEST_FILE == "" ]]; then
    echo "Error: test file is not specified!"
    print_help
    exit 1
fi

if [[ $RESULT_FILE == "" ]]; then
    echo "Error: result file is not specified!"
    print_help
    exit 1
fi

if [[ $COVERAGE_FILE == "" ]]; then
    echo "Error: code coverage file is not specified!"
    print_help
    exit 1
fi

if [[ $TIMEOUT -lt 0 ]]; then
    echo "Error: timeout is invalid or not specified!"
    print_help
    exit 1
fi

if [[ $TIME_DISTRIBUTION == "equal" ]]; then
    TIME_DISTRIBUTION_ARGS=" --time-distribute-equal "
fi

if [[ $CONTRACT_NAME != "" ]]; then
    CONTRACT_ARGS=" --contract-name $CONTRACT_NAME "
fi

################################################
# Configure paths

TOOL_DIR="/root/smartfuzz"

################################################
# Analyze input test files

# Run the first process of SmartFuzz to detect non-reentrancy bugs
python "$TOOL_DIR/main.py" $TEST_FILE -r $RESULT_FILE \
    -j 1 --time $TIMEOUT \
    -q --print-coverage $COVERAGE_FILE -s $RANDOM_SEED \
    $CONTRACT_ARGS $TIME_DISTRIBUTION_ARGS $ADDITIONAL_ARGS &

# Run the sencond process of SmartFuzz to detect reentrancy bugs
python "$TOOL_DIR/main.py" $TEST_FILE -r "$output_file.reentrancy" \
    -j 1 -q --time $TIMEOUT --reentrancy -s $RANDOM_SEED \
    $CONTRACT_ARGS $TIME_DISTRIBUTION_ARGS $ADDITIONAL_ARGS

# Wait and merge results from 2 processes
wait
python "$TOOL_DIR/scripts/merge_json_result.py" $RESULT_FILE
