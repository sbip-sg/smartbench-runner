#!/usr/bin/env bash

# Usage:
#   ./publish-tool-docker.sh -t <tool-ids>  [options]
#

################################################
# Some variables

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

SCRIPT_DIR="$(realpath $(dirname "$0"))"

################################################
# Usage

print_usage () {
    echo ""
    echo "Usage: "
    echo "  publish-tool-docker.sh -t <tool-ids> [options]"
    echo ""
    echo "Options:"
    echo "  -t <tool-id>            ID of analysis tool, currently support the followings:"
    echo "                          confuzzius, confuzzius-sbip, ilf, mythril, sfuzz,"
    echo "                          slither, smartfuzz, smartian."
    echo "                          Use `-t all` to install for all tools."
    echo "  --g2-user-name          Specify your user name in SBIP G2 server."
}

print_run_help () {
    echo ""
    echo "Please run with '-h' to see the command usage."
}

################################################
# Parse arguments

TOOL_IDS=()
G2_USER_NAME=""
TO_SBIP_G2=false
TO_DOCKERHUB=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -t)
            shift # past argument
            # Parse tool names
            while [[ $# -gt 0 ]]; do
                case $1 in
                    -*|--*)
                        break
                        ;;
                    *)
                        TOOL_IDS+=("$1")
                        shift  # past value
                        ;;
                esac
            done
            ;;
        --g2-user-name)
            G2_USER_NAME="$2"
            shift
            shift
            ;;
        --to-sbip-g2)
            TO_SBIP_G2=true
            shift
            ;;
        --to-dockerhub)
            TO_DOCKERHUB=true
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
    esac
done

# Checking tool ID
INSTALL_ALL_TOOLS=false
if [[ ${#TOOL_IDS[@]} == 0 ]]; then
    echo "Error: no analysis tool is specified!"
    print_run_help
    exit 1
else
    for TOOL_ID in ${TOOL_IDS[@]}; do
        if [[ $TOOL_ID == "all" ]]; then
            INSTALL_ALL_TOOLS=true
        elif [[ ! $(echo ${SUPPORTED_TOOLS[@]} | grep -w $TOOL_ID) ]]; then
            echo "Error: tool $TOOL_ID is not supported!"
            print_run_help
            exit 1
        fi
    done
fi

# Getting IDs of all tools to be published
if [[ $INSTALL_ALL_TOOLS == true ]]; then
    TOOL_IDS=(${SUPPORTED_TOOLS[@]})
fi

# Configure destination
if [[ $TO_SBIP_G2 == false && $TO_DOCKERHUB == false  ]]; then
    TO_SBIP_G2=true
    TO_DOCKERHUB=true
fi

################################################
# Publishing tool docker images

echo "Publishing Docker images of: ${TOOL_IDS[@]}"

if [[ $TO_SBIP_G2 == true && $G2_USER_NAME == "" ]]; then
    echo ""
    echo -n "Enter your username in SBIP G2: "
    read G2_USER_NAME
fi

for TOOL_ID in ${TOOL_IDS[@]}; do
    echo ""
    echo "------------------------------------"
    echo "Preparing Docker image for: $TOOL_ID"
    echo ""
    TOOL_LOCAL_IMAGE="smartbench/$TOOL_ID"
    TOOL_REMOTE_IMAGE="taquangtrung/$TOOL_ID"
    docker tag $TOOL_LOCAL_IMAGE $TOOL_REMOTE_IMAGE

    if [[ $TO_SBIP_G2 == true ]]; then
        TOOL_IMAGE_FILE="docker_image_${TOOL_ID}.tar.gz"
        TOOL_IMAGE_PATH=$SCRIPT_DIR/$TOOL_IMAGE_FILE
        echo "Saving Docker image to: $TOOL_IMAGE_PATH"
        echo ""
        docker save $TOOL_REMOTE_IMAGE | gzip > $TOOL_IMAGE_PATH
    fi

    if [[ $TO_DOCKERHUB == true ]]; then
        if [[ $TOOL_ID == "smartfuzz" ]]; then
            echo "Error: Smartfuzz should not be published to DockerHub!"
            echo ""
        else
            echo "Publishing $TOOL_ID's Docker image to DockerHub..."
            echo ""
            docker push $TOOL_REMOTE_IMAGE
        fi
    fi

    if [[ $TO_SBIP_G2 == true ]]; then
        echo "Publishing $TOOL_ID's Docker image SBIP G2..."
        echo ""
        scp $TOOL_IMAGE_PATH \
            $G2_USER_NAME@sbip-g2.d2.comp.nus.edu.sg:/users/trung/share/docker/$TOOL_IMAGE_FILE
    fi
done
