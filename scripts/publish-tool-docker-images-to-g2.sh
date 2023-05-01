#!/usr/bin/env bash

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
    echo "  publish-tool-docker-images-to-g2.sh -t <tool-ids> [options]"
    echo ""
    echo "Options:"
    echo "  -t <tool-id>            ID of analysis tool, currently support the followings:"
    echo "                            confuzzius, confuzzius-sbip, ilf, mythril, sfuzz,"
    echo "                            slither, smartfuzz, smartian."
    echo "                          Use `-t all` to install for all tools."
    echo "  --g2-user-name          Specify your user name in SBIP G2 server."
}

print_run_help () {
    echo ""
    echo "Please run with '-h' to see the command usage."
}

################################################
# Parse arguments

TOOL_ID=""
G2_USER_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t)
            TOOL_ID="$2"
            shift
            shift
            ;;
        --g2-user-name)
            G2_USER_NAME="$2"
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

# Getting IDs of all tools to be published
ALL_TOOL_IDS=()
if [[ $TOOL_ID == "all" ]]; then
    ALL_TOOL_IDS=(${SUPPORTED_TOOLS[@]})
else
    ALL_TOOL_IDS=($TOOL_ID)
fi

################################################
# Publishing tool docker images

if [[ $G2_USER_NAME == "" ]]; then
    echo -n "Enter your username in SBIP G2 to publish all tools' Docker images: "
    read G2_USER_NAME
fi

for TOOL_ID in ${ALL_TOOL_IDS[@]}; do
    echo ""
    echo "- Preparing Docker image for: $TOOL_ID"
    docker tag smartbench/$TOOL_ID taquangtrung/$TOOL_ID
    docker save taquangtrung/$TOOL_ID > docker_image_${TOOL_ID}.tar

    echo "  Publishing Docker image to SBIP G2: $TOOL_ID"
    scp docker_image_${TOOL_ID}.tar   $G2_USER_NAME@sbip-g2.d2.comp.nus.edu.sg:/users/trung/share/docker/docker_image_${TOOL_ID}.tar

done
