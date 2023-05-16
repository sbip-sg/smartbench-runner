#!/usr/bin/bash

# This script installs Docker container for smart contract analysis tools

SUPPORTED_TOOLS=(
    "confuzzius"
    "confuzzius-sbip"
    "ilf"
    "mythril"
    "sfuzz"
    "slither"
    "smartfuzz"
    "smartian"
)

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
    echo "  -t <tool-id>            ID of analysis tool, currently support the followings:"
    echo "                            confuzzius, confuzzius-sbip, ilf, mythril, sfuzz,"
    echo "                            slither, smartfuzz, smartian."
    echo "                          Use `-t all` to install for all tools."
    echo "  -n <num_of_containers>  Number of containers to be installed, which are named"
    echo "                          as {tool-id}-1, {tool-id}-2,..., {tool-id}-n."
    echo "  --force-install         Force install new containers."
    echo "  --base-image-no-cache   Build the base Smartbench Docker image without cache."
    echo "  --tool-image-no-cache   Build each tool Docker image without cache."
    echo "  --use-git-token         Enable reading GitHub access token during installation."
    echo "  --use-remote-images     Install tool Docker from the suitable remote (G2 or DockerHub)."
    echo "  --use-g2-images         Install tool Docker from images in G2."

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
INSTALL_LOCALLY=true
INSTALL_USING_G2=false
SBIP_G2_USER=""

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
        --use-remote-images)
            INSTALL_LOCALLY=false
            shift
            ;;
        --use-g2-images)
            INSTALL_LOCALLY=false
            INSTALL_USING_G2=true
            shift
            ;;
        --g2-user-name)
            SBIP_G2_USER="$2"
            shift
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
SCRIPT_DIR=$(realpath $(dirname "$0"))
SMARTBENCH_ROOT=$(dirname "$SCRIPT_DIR")
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

# Install base image of Smartbench locally
if [[ $INSTALL_LOCALLY == true ]]; then
    echo "============================================="
    echo "Building base image for all analysis tools..."
    echo ""

    BASE_CACHE_ARG=""
    if [[ $BASE_IMAGE_NO_CACHE == true ]]; then
        BASE_CACHE_ARG="--no-cache"
    fi

    cd $SMARTBENCH_ROOT
    docker build -f $SMARTBENCH_DOCKER_FILE -t $SMARTBENCH_DOCKER_IMAGE . $BASE_CACHE_ARG
fi

echo "============================================="
echo "Start building docker container(s) for: ${ALL_TOOL_IDS[@]}"
echo ""

# Configure some arguments to build Docker image for each tool locally or remotely
if [[ $INSTALL_LOCALLY == true ]]; then
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
fi

if [[ $INSTALL_USING_G2 == true || $TOOL_ID == "smartfuzz" ]] && [[ $SBIP_G2_USER == "" ]]; then
    echo -n "Enter your username in SBIP G2 to download Smartfuzz Docker image: "
    read SBIP_G2_USER
fi

for TOOL_ID in ${ALL_TOOL_IDS[@]}; do
    if [[ $INSTALL_LOCALLY == true ]]; then
        # Build Docker image for each tool locally

        echo "============================================="
        echo "Building Docker image for: $TOOL_ID..."
        echo ""

        # Get the root ID of a tool. Tool versions or variants should be
        # suffixed by `_` or `-`.
        TOOL_ROOT_ID=$(echo $TOOL_ID | sed 's/-.*//g')
        TOOL_ROOT_ID=$(echo $TOOL_ROOT_ID | sed 's/_.*//g')

        # Configure tool docker file and image
        TOOL_DIR="$SMARTBENCH_ROOT/smartbench/tools/$TOOL_ROOT_ID"
        TOOL_DOCKER_FILE="$TOOL_DIR/$TOOL_ID.Dockerfile"
        TOOL_DOCKER_IMAGE="smartbench/$TOOL_ID"
        docker build -f $TOOL_DOCKER_FILE -t $TOOL_DOCKER_IMAGE $GIT_TOKEN_ARG . $TOOL_CACHE_ARG
    elif [[ $INSTALL_USING_G2 == true || $TOOL_ID == "smartfuzz" ]]; then
        # Load Docker image from SBIP G2 server
        # This command below only works when running in NUS network

        echo "============================================="
        echo "Pulling Docker image from SBIP G2 for: $TOOL_ID..."
        echo ""

        TOOL_IMAGE_FILE="docker_image_$TOOL_ID.tar"
        TOOL_DOCKER_IMAGE="taquangtrung/$TOOL_ID"
        #rm -rf "/tmp/$TOOL_IMAGE_FILE"
        # docker load --input "/users/trung/share/docker/$TOOL_IMAGE_FILE"
        mkdir -p "/data/minh/"
        scp "$SBIP_G2_USER:/data/minh/$TOOL_IMAGE_FILE" \
                "/data/minh/$TOOL_IMAGE_FILE"
        docker load --input "/data/minh/$TOOL_IMAGE_FILE"
        # rm -rf "/tmp/$TOOL_IMAGE_FILE"
    else
        # Pull Docker image of other tools from DockerHub

        echo "============================================="
        echo "Pulling Docker image from DockerHub for: $TOOL_ID..."
        echo ""
        TOOL_DOCKER_IMAGE="taquangtrung/$TOOL_ID"
        docker pull $TOOL_DOCKER_IMAGE
    fi

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
    echo ""
    echo "============================================="
    echo "Creating docker containers: ${CONTAINER_NAMES[*]}"
    echo ""

    if $FORCE_INSTALL; then
        echo "Running force-install mode"
        echo ""
    fi

    for CONTAINER in "${CONTAINER_NAMES[@]}"; do
        echo "Checking container: $CONTAINER"
        if [[ $(docker ps -a -f name=$CONTAINER | grep -e "[ \t]$CONTAINER\$") ]]; then
            if $FORCE_INSTALL; then
                echo "A container named \"$CONTAINER\" already exists. Removing it ..."
                docker rm $CONTAINER --force
            elif [[ $(docker ps -f name=$CONTAINER | grep -e "[ \t]$CONTAINER\$") ]]; then
                echo "ERROR: a container named \"$CONTAINER\" is already running"
                echo "Please delete it and run this script again to continue a fresh installation!"
                echo ""
                clean_up 1
            else
                echo "ERROR: a container named \"$CONTAINER\" exists but is not running"
                echo "Please delete it and run this script again to continue a fresh installation!"
                echo ""
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
        echo ""
    done

    # Clean after installation
    clean_up 0

    echo "Installation succeeded!"
    echo "Run \"docker ps\" to see the newly launched Docker container "
done
