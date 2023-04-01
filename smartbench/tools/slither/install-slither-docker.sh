#!/usr/bin/env sh

# Usage: this script should be run from
#    ./install-slither-0.9.3-docker.sh

# Configure tool name
TOOL_ID="slither"
TOOL_NAME="Slither"

# Function for clean up after installation
clean_up_after_installation () {
    arg=$1
    echo "========================================"
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

echo "========================================"
echo "Install $TOOL_NAME in docker mode"
echo "Prepare environments..."

# Prepare environments
TOOL_DIR=$(realpath $(dirname "$0"))
SMARTBENCH_ROOT=$(dirname $(dirname $(dirname "$TOOL_DIR")))
BENCHMARKS_DIR="$SMARTBENCH_ROOT/benchmarks"
EXAMPLES_DIR="$SMARTBENCH_ROOT/examples"
RESULTS_DIR="$SMARTBENCH_ROOT/results"

# Prepare some names
IMAGE_NAME="smartbench/$TOOL_ID"
CONTAINER_NAME="$TOOL_ID"

cd $TOOL_DIR

# Prepare some examples to copy to Docker image
mkdir examples
cp ../../../examples/*.sol examples

# Build Docker image
echo "========================================"
echo "Building Docker image for $TOOL_NAME..."
docker build -f slither.dockerfile -t $IMAGE_NAME .

# Create a new Docker container that share the two folders:
# `benchmarks` and `results` with the host system.
echo "========================================"
echo "Launching Docker container..."
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    if [ ! "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
        echo "ERROR: a container named \"$CONTAINER_NAME\" is already running"
        echo "Please turn off and delete it first!"
        clean_up_after_installation 1
    else
        echo "ERROR: a container named \"$CONTAINER_NAME\" exists but is not running"
        echo "Please delete it first!"
        clean_up_after_installation 1
    fi
fi

# run your container
docker run -itd \
    --name $CONTAINER_NAME \
    -v $BENCHMARKS_DIR:/root/benchmarks \
    -v $RESULTS_DIR:/root/results \
    $IMAGE_NAME

# Clean after installation
clean_up_after_installation 0

echo "Installation succeeded!"
echo "Run \"docker ps\" to see the newly launched Docker container "
