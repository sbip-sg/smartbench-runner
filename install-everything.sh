#!/usr/bin/env sh

echo ""
echo "======================================================"
echo "Install Smartbench environment"
echo ""
./install-smartbench-env.sh

echo ""
echo "======================================================"
echo "Install all Docker containers"
echo ""
./install-tool-docker.sh -t all -n 30 --use-remote-images --force-install
