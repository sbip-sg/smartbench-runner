#!/bin/bash

# Usage:
#   ./run-smartian.sh <test-file> [-c <contract names>] [additional-smartian-arguments]
#
# NOTE:
#   - Test file must be the first argument
#   - Contract names are whitespace-separated
#   - This script must be configured so that it can be used both to run
#     in a Docker container as well as to run locally.
#

# Arguments of Smartian
TEST_FILE=$(realpath $1)
shift  # Past test file

CONTRACT_NAMES=()
ADDITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
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
        *)
            ADDITIONAL_ARGS+=("$1") # save all other arguments
            shift # past argument
            ;;
    esac
done

# Configure tool path when running inside or outside a Docker container.
if [ -f /.dockerenv ]; then
    TOOL_ROOT_PATH="/root/smartian"
else
    TOOL_ROOT_PATH="$(realpath $(dirname "$0"))/repo/smartian"
fi

# Detect Solc version to be used.
SOLC_VER=$(solc-detect $TEST_FILE)

# Compile test file to contracts in ABI and BIN format
COMPILED_CONTRACTS="compiled_contracts"
rm -rf $COMPILED_CONTRACTS
mkdir $COMPILED_CONTRACTS
SOLC_VERSION=$SOLC_VER solc $TEST_FILE --bin --abi \
    -o $COMPILED_CONTRACTS --overwrite \
    1>/dev/null 2>&1

if [[ ${#CONTRACT_NAMES[@]}  == 0 ]]; then
    CURRENT_DIR=$(pwd)
    cd $COMPILED_CONTRACTS
    CONTRACT_NAMES=($(ls -1 *.bin | sed "s/\.bin//"))
    cd $CURRENT_DIR
fi

# Run Smartian on each candidate contract
for CONTRACT in $CONTRACT_NAMES; do
    echo "==============================="
    echo "* Fuzzing contract: $CONTRACT"
    dotnet $TOOL_ROOT_PATH/build/Smartian.dll fuzz \
        --useothersoracle --checkoptionalbugs --verbose 1 \
        --program "$COMPILED_CONTRACTS/$CONTRACT.bin" \
        --abifile "$COMPILED_CONTRACTS/$CONTRACT.abi" \
        ${ADDITIONAL_ARGS[@]}
done
