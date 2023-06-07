#!/bin/bash

csv_folder="run3/benchmarks/real-hacks/"

# Array of bug types
bug_types=(
"Lack of Zero-Address Validation"
"REENTRANCY,"
"Integer Truncation"
"Block Values Dependency \(BlockValueDependencySensitive\)"
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

    # Search for the bug type, remove blank lines, shuffle the results, take the top 50, and write to a file
    rg -I -tcsv "$bug_type" "$csv_folder" | grep -v '{' | shuf | head -n 50 > "50_${filename}.csv"
done
