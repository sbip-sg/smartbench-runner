#!/bin/bash

FILENAME="$1"
# BIN="$2"
# TIMEOUT="$2"
# MAIN="$3"

# export PATH="$BIN:$PATH"
# chmod +x "$BIN"

CONTRACT="${FILENAME%.sol}"
CONTRACT="${CONTRACT##*/}"
CONTRACTS=$(python3 smartbench/tools/sfuzz/printContractNames.py "$FILENAME")
COUNT=$(echo $CONTRACTS | wc -w)
[ "$COUNT" -gt 0 ] || COUNT=1

# if (echo "$CONTRACTS" | grep -q "$CONTRACT"); then
#     CONTRACTS="$CONTRACT"
#     COUNT=1
# else
#     echo "Contract '$CONTRACT' not found in $FILENAME"
#     exit 127
# fi

cd smartbench/tools/sfuzz/sFuzz/build/fuzzer/
rm -rf contracts
mkdir contracts

for CONTRACT in $CONTRACTS; do
    echo "Extract contract $CONTRACT from $FILENAME"
    cp "$FILENAME" "contracts/$CONTRACT.sol"
done

echo "Extracted $COUNT contract(s) from $FILENAME"

# Fuzz each contract at least 10 seconds
# TO=$(((TIMEOUT - (2 * COUNT)) / COUNT))
# if [ "$TIMEOUT" -eq 0 ] || [ $TO -lt 10 ]; then
#     TO=120
# fi

./fuzzer -g -r 1 -d 20 && chmod +x fuzzMe && ./fuzzMe
