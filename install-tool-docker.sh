#!/usr/bin/bash

# This script installs Docker container for smart contract analysis tools

SUPPORTED_TOOLS=("slither" "sfuzz" "confuzzius" "smartian" "smartfuzz" "ilf" "mythril")

SUPPORTED_TOOL_IDS=${SUPPORTED_TOOLS[@]}
SUPPORTED_TOOL_IDS+=("all")

################################################
# Usage

print_usage () {
    echo ""
    echo "Usage: "
    echo "  install-tool-docker.sh -t <tool-ids> [options] [container_1, ... , container_n]"
    echo ""
    echo "Options:"
    echo "  -t <tool-id>               ID of analysis tool, currently support the followings:"
    echo "                             $(echo ${SUPPORTED_TOOL_IDS[@]} | sed 's/ /, /g') "
    echo "  -n <number_of_containers>  Number of containers to be installed, which are named"
    echo "                             as {tool-id}-1, {tool-id}-2,..., {tool-id}-n."
    echo "  --force-install            Force install new containers."
    echo "  --base-image-no-cache      Build the base Smartbench Docker image without cache."
    echo "  --tool-image-no-cache      Build each tool Docker image without cache."
    echo "  --use-git-token            Enable reading GitHub access token during installation."
}

print_run_help () {
    echo ""
    echo "Please run with '-h' to see the command usage."
}

################################################
# Parse arguments

TOOL_ID=""
CONTAINER_NAMES=()
NUM_CONTAINERS=0
FORCE_INSTALL=false
BASE_IMAGE_NO_CACHE=false
TOOL_IMAGE_NO_CACHE=false
USE_GIT_TOKEN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -t)
            TOOL_ID="$2"
            shift
            shift
            ;;
        -n)
            NUM_CONTAINERS=$2
            shift
            shift
            ;;
        --use-git-token)
            USE_GIT_TOKEN=true
            shift
            ;;
        --force-install)
            FORCE_INSTALL=true
            shift
            ;;
        --base-image-no-cache)
            BASE_IMAGE_NO_CACHE=true
            shift
            ;;
        --tool-image-no-cache)
            TOOL_IMAGE_NO_CACHE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 1
            ;;
        -*|--*)
            echo "Error: unknown option $1"
            print_run_help
            exit 1
            ;;
        *)
            CONTAINER_NAMES+=("$1") # save positional args as container names
            shift
            ;;
    esac
done

# Checking tool ID
if [[ $TOOL_ID == "" ]]; then
    echo "Error: analysis tool ID is not specified!"
    print_run_help
    exit 1
elif [[ ! $(echo ${SUPPORTED_TOOL_IDS[@]} | grep -w $TOOL_ID) ]]; then
    echo "Error: tool $TOOL_ID is not supported!"
    print_run_help
    exit 1
fi

# Getting IDs of all tools to be built
ALL_TOOL_IDS=()
if [[ $TOOL_ID == "all" ]]; then
    ALL_TOOL_IDS=(${SUPPORTED_TOOLS[@]})
else
    ALL_TOOL_IDS=($TOOL_ID)
fi

# Checking container names
if [[ $NUM_CONTAINERS == "" ]]; then
    echo "Error: invalid number of containers!"
    print_run_help
    exit 1
fi

if [[ ${#ALL_TOOL_IDS[@]} > 1 && ${#CONTAINER_NAMES[@]} > 0 ]]; then
    echo "Do not specify container name '${CONTAINER_NAMES[@]}' when building for multiple tools!"
    print_run_help
    exit 1
fi

################################################
# Handling errors

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

    if [[ ! $arg -eq 0 ]]; then
        echo "Abort installation!"
        exit 1
    fi
}

# Clean up when error occur
trap "clean_up 1" ERR

################################################

# Smartbench directories
SMARTBENCH_ROOT=$(realpath $(dirname "$0"))
SMARTBENCH_BENCHMARKS_DIR="$SMARTBENCH_ROOT/benchmarks"
SMARTBENCH_EXAMPLES_DIR="$SMARTBENCH_ROOT/examples"
SMARTBENCH_RESULTS_DIR="$SMARTBENCH_ROOT/results"
SMARTBENCH_DOCKER_FILE="$SMARTBENCH_ROOT/smartbench/tools/smartbench.Dockerfile"
SMARTBENCH_DOCKER_IMAGE="smartbench/base"

# Docker container directories
DOCKER_BENCHMARKS_DIR="/root/benchmarks"
DOCKER_EXAMPLES_DIR="/root/examples"
DOCKER_RESULTS_DIR="/root/results"

# Build base Docker image
echo "Start building docker containers for analysis tools... "
echo ""
echo "============================================="
echo "Building base image for all analysis tools..."
echo ""

BASE_CACHE_ARG=""
if [[ $BASE_IMAGE_NO_CACHE == true ]]; then
    BASE_CACHE_ARG="--no-cache"
fi

cd $SMARTBENCH_ROOT
docker build -f $SMARTBENCH_DOCKER_FILE -t $SMARTBENCH_DOCKER_IMAGE . $BASE_CACHE_ARG

echo ""
echo "============================================="
echo "Start building docker container(s) for: ${ALL_TOOL_IDS[@]}"
echo ""

TOOL_CACHE_ARG=""
if [[ $TOOL_IMAGE_NO_CACHE == true ]]; then
    TOOL_CACHE_ARG="--no-cache"
fi

GIT_TOKEN_ARG=""
if [[ $USE_GIT_TOKEN == true ]]; then
    echo "Git Access Token is required to build Docker image from: $TOOL_DOCKER_FILE"
    echo -n "Enter your Git Access Token: "
    read GIT_TOKEN
    GIT_TOKEN_ARG=" --build-arg GIT_ACCESS_TOKEN=$GIT_TOKEN"
fi

for TOOL_ID in ${ALL_TOOL_IDS[@]}; do
    # Tool directories
    TOOL_DIR="$SMARTBENCH_ROOT/smartbench/tools/$TOOL_ID"

    # Docker information
    TOOL_DOCKER_FILE="$TOOL_DIR/$TOOL_ID.Dockerfile"
    TOOL_DOCKER_IMAGE="smartbench/$TOOL_ID"

    # Build Docker image
    echo "============================================="
    echo "Building Docker image for: $TOOL_ID..."
    echo ""

    docker build -f $TOOL_DOCKER_FILE -t $TOOL_DOCKER_IMAGE $GIT_TOKEN_ARG . $TOOL_CACHE_ARG

    # Clear previous containers names if building for many tools
    if [[ ${#ALL_TOOL_IDS[@]} > 1 ]]; then
       CONTAINER_NAMES=()
    fi

    # Generate new container names
    for ((i=1; i<=$NUM_CONTAINERS; i++)); do
        CONTAINER_NAMES+=("$TOOL_ID-$i")
    done

    if [[ ${#CONTAINER_NAMES[@]} == 0 ]]; then
        echo "Error: no container name or number of container is specified!"
        print_run_help
        exit 1
    fi

    # Create new Docker containers that share the two folders:
    # `benchmarks` and `results` with the host system.
    echo "============================================="
    echo "Creating docker containers: ${CONTAINER_NAMES[*]}"
    echo ""

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
        echo ""
        echo "Installing container \"$CONTAINER\" ..."
        docker run -itd \
            --name $CONTAINER \
            -v $SMARTBENCH_BENCHMARKS_DIR:$DOCKER_BENCHMARKS_DIR \
            -v $SMARTBENCH_RESULTS_DIR:$DOCKER_RESULTS_DIR \
            $TOOL_DOCKER_IMAGE
    done

    # Clean after installation
    clean_up 0

    echo "Installation succeeded!"
    echo "Run \"docker ps\" to see the newly launched Docker container "
done
