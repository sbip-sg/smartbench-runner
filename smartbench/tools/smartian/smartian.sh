#!/bin/bash

FILENAME="$1"
TIMEOUT="$2"
VERSION="$3"

TOOL_ID="smartian"
BASE_DIR=$(dirname "$0")
REPO_DIR=$BASE_DIR"/repo"
TOOL_DIR=$REPO_DIR/$TOOL_ID

cd $TOOL_DIR
mkdir output
mkdir input
solc-select install $VERSION
solc-select use $VERSION

CONTRACT="${FILENAME%.sol}"
CONTRACT="${CONTRACT##*/}"
CONTRACTS=$(python3 smartbench/tools/smartian/printContractNames.py "$FILENAME")
COUNT=$(echo $CONTRACTS | wc -w)
EACH_TIMEOUT = $TIMEOUT/$COUNT

for CONTRACT in $CONTRACTS; do
    dotnet build/Smartian.dll fuzz -p input/$CONTRACT.bin  -a input/$CONTRACT. -t $EACH_TIMEOUT -o output
done

