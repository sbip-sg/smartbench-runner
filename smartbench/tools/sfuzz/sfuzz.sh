#!/bin/bash

FILENAME="$1"
TIMEOUT="$2"
VERSION="$3"

CONTRACT="${FILENAME%.sol}"
CONTRACT="${CONTRACT##*/}"
CONTRACTS=$(python3 smartbench/tools/printContractNames.py "$FILENAME")

TOOL_ID="sfuzz"
BASE_DIR=$(dirname "$0")
REPO_DIR=$BASE_DIR"/repo"
TOOL_DIR=$REPO_DIR/$TOOL_ID

cd $TOOL_DIR/build/fuzzer/
rm -rf contracts
mkdir contracts
rm -rf output
mkdir output

for CONTRACT in $CONTRACTS; do
    echo "Extract contract $CONTRACT from $FILENAME"
    cp "$FILENAME" "contracts/$CONTRACT.sol"
done

solc-select install $VERSION
solc-select use $VERSION

./fuzzer -g -r 0 -d $TIMEOUT --attacker ReentrancyAttacker > $4 2>&1
chmod +x fuzzMe
./fuzzMe
