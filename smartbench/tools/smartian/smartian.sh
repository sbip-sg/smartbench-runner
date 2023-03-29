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
solc-select install $VERSION
solc-select use $VERSION

CONTRACT="${FILENAME%.sol}"
CONTRACT="${CONTRACT##*/}"
CONTRACTS=$(python3 smartbench/tools/sfuzz/printContractNames.py "$FILENAME")

dotnet build/Smartian.dll fuzz -p <bytecode file> -a <abi file> -t <time limit> -o output

