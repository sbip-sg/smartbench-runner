#!/usr/bin/env sh

# Root directory
BASE_DIR="$(realpath $(dirname "$0"))"

echo ""
echo "===================================="
echo "Update Smartbench source code"
echo ""
git pull --recurse-submodules

echo ""
echo "===================================="
echo "Update Smartbench dataset"
echo ""
cd $BASE_DIR/benchmarks/smartbench-dataset && git checkout main && git pull

echo ""
echo "===================================="
echo "Update Smartbench results"
echo ""
cd $BASE_DIR/results/smartbench-results && git checkout main && git pull
