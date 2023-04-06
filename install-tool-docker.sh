#!/usr/bin/bash

# This script installs Docker container for all analysis tools

# Usage:
#   ./install-tool-docker.sh <TOOL-ID> [CONTAINER_NAME] [-n <NUMBER-OF-CONTAINERS>]
#
# Example:
#   # Install the default container named `slither`
#   ./install-tool-docker.sh slither
#
#   # Install a container named `slither-analyzer`
#   ./install-tool-docker.sh slither slither-analyzer
#
#   # Install 5 containers: `slither-1`, ..., `slither-5`
#   ./install-tool-docker.sh slither -n 5

print_usage () {
    echo ""
    echo "Usage: "
    echo "  install-tool-docker.sh <TOOL-ID> [CONTAINER_NAME] [-n <NUMBER-OF-CONTAINERS>]"
    echo ""
    echo "Examples:"
    echo "  install-tool-docker.sh slither"
    echo "  install-tool-docker.sh slither slither-analyzer"
    echo "  install-tool-docker.sh slither -n 5"
}

if [[ $# == 0 ]]; then
    echo "No argument is provided"
    print_usage
    exit 1
fi

# Tool ID
TOOL_ID="$1"

# Smartbench directories
SMARTBENCH_ROOT=$(realpath $(dirname "$0"))
SMARTBENCH_BENCHMARKS_DIR="$SMARTBENCH_ROOT/benchmarks"
SMARTBENCH_EXAMPLES_DIR="$SMARTBENCH_ROOT/examples"
SMARTBENCH_RESULTS_DIR="$SMARTBENCH_ROOT/results"

# Tool directories
TOOL_DIR="$SMARTBENCH_ROOT/smartbench/tools/$TOOL_ID"
TOOL_EXAMPLES_DIR="$TOOL_DIR/examples"

# Docker information
DOCKER_FILE="$TOOL_DIR/$TOOL_ID.Dockerfile"
DOCKER_IMAGE="smartbench/$TOOL_ID"

# Containers to be installed
if [[ -z "$2" ]]; then
    DOCKER_CONTAINERS="$TOOL_ID"      # default container name
elif [[ $2 == "-n" ]]; then
    if [[ -z "$3" ]]; then
        echo "Number of containers is not provided!"
        print_usage
        exit 1
    else
        NUM_CONTAINERS=$3
        DOCKER_CONTAINERS=""
        for ((i=1;i<=$NUM_CONTAINERS;i++)); do
            DOCKER_CONTAINERS="$DOCKER_CONTAINERS$TOOL_ID-$i "
        done
    fi
    echo "CONTAINERS: $DOCKER_CONTAINERS"
else
    DOCKER_CONTAINERS="${@:2}"        # get container names from arguments
fi

# Docker container directories
DOCKER_BENCHMARKS_DIR="/root/benchmarks"
DOCKER_EXAMPLES_DIR="/root/examples"
DOCKER_RESULTS_DIR="/root/results"

# Quit on error during installation
set -e

clean_up () {
    arg=$1
    echo "============================================="
    if [[ $arg -eq 0 ]]; then
        echo "Cleaning after installation..."
    else
        echo "Cleaning after error..."
    fi

    rm -rf examples

    if [[ ! $arg -eq 0 ]]; then
        echo "Abort installation!"
        exit 1
    fi
}

# Clean up when error occur
trap "clean_up 1" ERR

echo "============================================="
echo "Install $TOOL_NAME in docker mode"
echo "Prepare environments..."

# Prepare some examples to copy to Docker image
cd $TOOL_DIR
mkdir $TOOL_EXAMPLES_DIR
cp $SMARTBENCH_EXAMPLES_DIR/*.sol $TOOL_EXAMPLES_DIR

# Build Docker image
echo "============================================="
echo "Building Docker image for $TOOL_NAME..."
docker build -f $DOCKER_FILE -t $DOCKER_IMAGE .

# Create a new Docker container that share the two folders:
# `benchmarks` and `results` with the host system.
echo "============================================="
for CONTAINER in $DOCKER_CONTAINERS; do
    echo "Create and launch a Docker container: $CONTAINER"
    if [[ $(docker ps -a -f name=$CONTAINER | grep -e "[ \t]$CONTAINER\$") ]]; then
        if [[ $(docker ps -f name=$CONTAINER | grep -e "[ \t]$CONTAINER\$") ]]; then
            echo "ERROR: a container named \"$CONTAINER\" is already running"
            echo "Please delete it and run this script again to continue a fresh installation!"
            clean_up 1
        else
            echo "ERROR: a container named \"$CONTAINER\" exists but is not running"
            echo "Please delete it and run this script again to continue a fresh installation!"
            clean_up 1
        fi
    fi

    # run your container
    docker run -itd \
        --name $CONTAINER \
        -v $SMARTBENCH_BENCHMARKS_DIR:$DOCKER_BENCHMARKS_DIR \
        -v $SMARTBENCH_RESULTS_DIR:$DOCKER_RESULTS_DIR \
        $DOCKER_IMAGE
done

# Clean after installation
clean_up 0

echo "Installation succeeded!"
echo "Run \"docker ps\" to see the newly launched Docker container "
