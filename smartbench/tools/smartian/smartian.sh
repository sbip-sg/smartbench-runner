#!/bin/bash

FILENAME="$1"
TOTAL_TIMEOUT="$2"
VERSION="$3"

TOOL_ID="smartian"
BASE_DIR=$(dirname "$0")
REPO_DIR=$BASE_DIR"/repo"
TOOL_DIR=$REPO_DIR/$TOOL_ID

CONTRACT="${FILENAME%.sol}"
CONTRACT="${CONTRACT##*/}"
CONTRACTS=$(python3 smartbench/tools/printContractNames.py "$FILENAME")
COUNT=$(echo $CONTRACTS | wc -w)
TIMEOUT=$((TOTAL_TIMEOUT / COUNT))

cd $TOOL_DIR
rm -rf input
rm -rf output
mkdir output
mkdir input
solc-select install $VERSION
solc-select use $VERSION
solc --bin --abi $1 -o input --overwrite

for CONTRACT in $CONTRACTS; do
    dotnet build/Smartian.dll fuzz --useothersoracle --checkoptionalbugs --verbose 1 --program input/$CONTRACT.bin --abifile input/$CONTRACT.abi -t $TIMEOUT -o output > $4 2>&1
done

