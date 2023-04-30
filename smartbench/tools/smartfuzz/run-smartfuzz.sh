#!/bin/bash
# running benchmark ./benchmark.sh input_file output_file timeout seed
# copy from smartfuzz/scripts/benchmark.sh
if test "$#" -lt 6; then
    echo "Taking at least 6 parameters"
    echo "./benchmark.sh input_file output_file coverage_file timeout[integer] seed[integer] time_distribution[equal or default] [the rest]"
    echo "example ./benchmark.sh test.sol test.out.json test.out.coverage.json 10 1 default [other smartfuzz args --contract-name Test]"
    exit 0
fi
input_file=$1
output_file=$2
coverage_file=$3
timeout=$4
seed=$5
time_distribution=$6
time_distribution_args=""
if [[ "$time_distribution" == "equal" ]]; then
    time_distribution_args=" --time-distribute-equal "
fi
if [[ "$output_file" == "automatic" ]]; then
    output_file="$input_file.result.json"
fi
if [ -f /.dockerenv ]; then
    TOOL_DIR="/root/smartfuzz"
else
    TOOL_DIR="$(realpath $(dirname "$0"))/repo/smartfuzz"
fi

# Shift the arguments to the left by 6 to remove the first 6 arguments
shift 6
# disable --use-symbolic-execution for now
# move --use-dependency-graph --use-delta-debugging --enable-abstract-rewriting to upper level script
python "$TOOL_DIR/main.py" $input_file -r $output_file -j 1 --time $timeout -q --print-coverage $coverage_file -s $seed $time_distribution_args $@ &
python "$TOOL_DIR/main.py" $input_file -r "$output_file.reentrancy" -j 1 -q --time $timeout --reentrancy -s $seed $time_distribution_args $@
wait
python "$TOOL_DIR/scripts/merge_json_result.py" $output_file
