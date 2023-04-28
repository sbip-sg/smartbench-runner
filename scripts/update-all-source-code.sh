#!/usr/bin/env sh

# Root directory
SCRIPT_DIR="$(realpath $(dirname "$0"))"
SMARTBENCH_ROOT=$(dirname "$SCRIPT_DIR")

cd $SMARTBENCH_ROOT
echo ""
echo "===================================="
echo "Update Smartbench source code"
echo ""
git pull --recurse-submodules

echo ""
echo "===================================="
echo "Update Smartbench dataset"
echo ""
cd $SMARTBENCH_ROOT/benchmarks/smartbench-dataset && git checkout main && git pull

echo ""
echo "===================================="
echo "Update Smartbench results"
echo ""
cd $SMARTBENCH_ROOT/results/smartbench-results && git checkout main && git pull
