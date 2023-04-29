#!/usr/bin/env sh

INPUT_DIR=$1


echo "Removing ansi color in log files..."

for file in $(find $INPUT_DIR -name "*.log"); do
    echo "- $file"
    # sed -i "s/\\/part_[^\\/]*\\//\\//g" $file
    sed -i "s/benchmarks\\/B/benchmarks\\/smartbench-dataset\\/solidity\\/smartian\\/B/g" $file
done

echo "Done!"
