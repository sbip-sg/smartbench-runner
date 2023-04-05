#!/usr/bin/bash

# Usage: this script should be run from
#    ./install-slither-docker.sh [container_name_1] [container_name_2] ...
#
# Example:
#    ./install-slither-docker.sh
#    ./install-slither-docker.sh slither-1 slither-2 slither-3


# Tool name and ID
TOOL_ID="slither"
TOOL_NAME="Slither"

# Tool directories
TOOL_DIR=$(realpath $(dirname "$0"))
TOOL_EXAMPLES_DIR="$TOOL_DIR/examples"

# Host directories
SMARTBENCH_ROOT=$(dirname $(dirname $(dirname "$TOOL_DIR")))
HOST_BENCHMARKS_DIR="$SMARTBENCH_ROOT/benchmarks"
HOST_EXAMPLES_DIR="$SMARTBENCH_ROOT/examples"
HOST_RESULTS_DIR="$SMARTBENCH_ROOT/results"

# Docker image
DOCKER_IMAGE="smartbench/$TOOL_ID"

# Containers to be installed
if [ -z "$1" ]; then
    DOCKER_CONTAINERS="$TOOL_ID"      # default container name
else
    DOCKER_CONTAINERS="${@:1}"        # from argument inputs of this script
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
cp $HOST_EXAMPLES_DIR/*.sol $TOOL_EXAMPLES_DIR

# Build Docker image
echo "============================================="
echo "Building Docker image for $TOOL_NAME..."
docker build -f slither.Dockerfile -t $DOCKER_IMAGE .

# Create a new Docker container that share the two folders:
# `benchmarks` and `results` with the host system.
echo "============================================="
for CONTAINER in $DOCKER_CONTAINERS; do
    echo "Create and launch a Docker container: $CONTAINER"
    if [ "$(docker ps -a -f name=$CONTAINER | grep -w $CONTAINER)" ]; then
        if [ ! "$(docker ps -aq -f status=exited -f name=$CONTAINER)" ]; then
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
        -v $HOST_BENCHMARKS_DIR:$DOCKER_BENCHMARKS_DIR \
        -v $HOST_RESULTS_DIR:$DOCKER_RESULTS_DIR \
        $DOCKER_IMAGE
done

# Clean after installation
clean_up 0

echo "Installation succeeded!"
echo "Run \"docker ps\" to see the newly launched Docker container "
