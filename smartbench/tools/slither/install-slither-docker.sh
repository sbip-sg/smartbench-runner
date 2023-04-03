#!/usr/bin/env bash

# Usage: this script should be run from
#    ./install-slither-docker.sh

# Configure script
set -e                 # Quit on the first error

# Function for clean up after installation
clean_up () {
    arg=$1
    echo "============================================="
    if [ $arg -eq 0 ]; then
        echo "Cleaning after installation..."
    else
        echo "Cleaning after error..."
    fi

    rm -rf examples

    if [ ! $arg -eq 0 ]; then
        echo "Abort installation!"
        exit 1
    fi
}

trap "clean_up 1" ERR

# Configure tool name
TOOL_ID="slither"
TOOL_NAME="Slither"
CONFIG_FILE="$TOOL_ID.toml"


# Tool directories
TOOL_DIR=$(realpath $(dirname "$0"))
TOOL_EXAMPLES_DIR="$TOOL_DIR/examples"

# Host directories
SMARTBENCH_ROOT=$(dirname $(dirname $(dirname "$TOOL_DIR")))
HOST_BENCHMARKS_DIR="$SMARTBENCH_ROOT/benchmarks"
HOST_EXAMPLES_DIR="$SMARTBENCH_ROOT/examples"
HOST_RESULTS_DIR="$SMARTBENCH_ROOT/results"

# Docker directories
DOCKER_IMAGE=$(grep "image_name" slither.toml | sed "s/.*=//" | xargs)
DOCKER_CONTAINER=$(grep "container_name" slither.toml | sed "s/.*=//" | xargs)
DOCKER_BENCHMARKS_DIR=$(grep "benchmarks_dir" slither.toml | sed "s/.*=//" | xargs)
DOCKER_EXAMPLES_DIR=$(grep "examples_dir" slither.toml | sed "s/.*=//" | xargs)
DOCKER_RESULTS_DIR=$(grep "results_dir" slither.toml | sed "s/.*=//" | xargs)

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
echo "Launching Docker container..."
if [ "$(docker ps -a -f name=$DOCKER_CONTAINER | grep -w $DOCKER_CONTAINER)" ]; then
    if [ ! "$(docker ps -aq -f status=exited -f name=$DOCKER_CONTAINER)" ]; then
        echo "ERROR: a container named \"$DOCKER_CONTAINER\" is already running"
        echo "Please delete it and run this script again to continue a fresh installation!"
        clean_up 1
    else
        echo "ERROR: a container named \"$DOCKER_CONTAINER\" exists but is not running"
        echo "Please delete it and run this script again to continue a fresh installation!"
        clean_up 1
    fi
fi

# run your container
docker run -itd \
    --name $DOCKER_CONTAINER \
    -v $HOST_BENCHMARKS_DIR:$DOCKER_BENCHMARKS_DIR \
    -v $HOST_RESULTS_DIR:$DOCKER_RESULTS_DIR \
    $DOCKER_IMAGE

# Clean after installation
clean_up 0

echo "Installation succeeded!"
echo "Run \"docker ps\" to see the newly launched Docker container "
