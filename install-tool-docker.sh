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

##############################
# Parse arguments

# Tool ID
TOOL_ID="$1"
shift

CONTAINER_NAMES=()
NUM_CONTAINERS=0
FORCE_INSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -n)
            NUM_CONTAINERS=$2
            shift # past argument
            shift # past value
            ;;
        --force-install)
            FORCE_INSTALL=true
            shift # past argument
            ;;
        -*|--*)
            echo "Unknown option $1"
            print_usage
            exit 1
            ;;
        *)
            CONTAINER_NAMES+=("$1") # save positional args as container names
            shift # past argument
            ;;
    esac
done

##############################


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

# Docker containers to be installed
for ((i=1; i<=$NUM_CONTAINERS; i++)); do
    CONTAINER_NAMES+=("$TOOL_ID-$i")
done

if [[ ${#CONTAINER_NAMES[@]} == 0 ]]; then
    CONTAINER_NAMES=($TOOL_ID)
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
echo "Creating docker containers: ${CONTAINER_NAMES[*]}"

if $FORCE_INSTALL; then
    echo "Running force-install mode"
fi

for CONTAINER in "${CONTAINER_NAMES[@]}"; do
    echo ""
    echo "Checking container: $CONTAINER"
    if [[ $(docker ps -a -f name=$CONTAINER | grep -e "[ \t]$CONTAINER\$") ]]; then
        if $FORCE_INSTALL; then
            echo "A container named \"$CONTAINER\" already exists. Removing it ..."
            docker rm $CONTAINER --force
        elif [[ $(docker ps -f name=$CONTAINER | grep -e "[ \t]$CONTAINER\$") ]]; then
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
    echo "Running the new container ..."
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
