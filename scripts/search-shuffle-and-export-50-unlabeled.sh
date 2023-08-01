#!/bin/bash

csv_folder="run3/benchmarks/real-hacks/"

# Array of bug types
bug_types=(
"Lack of Zero-Address Validation"
"REENTRANCY,"
"Integer Truncation"
# "BlockValueDependencySensitive,"
"Integer Overflow"
"Integer Underflow"
"REENTRANCY_READONLY"
"ERC20 Access Control"
"Access Control"
"Unhandled Exception"
"Unchecked Send Ether"
"ERC20 Leak"
"IntegerDivByZero by YUL"
"BlockValueDependency,"
"Authorization through tx.origin"
"Arbitrary External Call"
"Locking Ether"
"Assertion Failure"
"Denial of Service"
"Unsafe DelegateCall"
)

# Loop over each bug type
for bug_type in "${bug_types[@]}"; do
    # Replace spaces and parentheses in the bug type with underscores to create a valid filename
    filename=$(echo "$bug_type" | tr ' ' '_' | tr '(' '_' | tr ')' '_')

    # search bug type, ignore summaries (line with `{`), shuffle, take 50, then sort again
    # rg -I -tcsv "Lack of Zero-Address Validation" "run3/benchmarks/real-hacks/" | grep -v '{' | shuf | head -n 60  | sort
    # rg -I -tcsv "BlockValueDependencySensitive," "run3/benchmarks/real-hacks/" | grep -v '{' | shuf | head -n 60  | sort  > "50_BlockValueDependencySensitive.csv"
    # rg -I -tcsv "ERC20 Leak," "run2/benchmarks/real-hacks/" | grep -v '{' | shuf | head -n 60  | sort  > "50_ERC20_Leak.csv"
    rg -I -tcsv "$bug_type" "$csv_folder" | grep -v '{' | shuf | head -n 50  | sort > "50_${filename}.csv"
done
