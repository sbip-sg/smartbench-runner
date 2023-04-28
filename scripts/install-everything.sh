#!/usr/bin/env sh

SCRIPT_DIR=$(dirname "$0")

echo ""
echo "======================================================"
echo "Install Smartbench environment"
echo ""
$SCRIPT_DIR/install-smartbench-env.sh

echo ""
echo "======================================================"
echo "Install all Docker containers"
echo ""
$SCRIPT_DIR/install-tool-docker.sh -t all -n 30 --use-remote-images --force-install
