#!/usr/bin/env bash

echo -n "Enter your username in SBIP G2 to publish all tools' Docker images: "
read SBIP_G2_USER

echo "- Preparing Docker image for: smartfuzz"
docker tag smartbench/smartfuzz taquangtrung/smartfuzz
docker save taquangtrung/smartfuzz > docker_image_smartfuzz.tar

echo "  Publishing Docker image to SBIP G2: smartfuzz"
scp docker_image_smartfuzz.tar  $SBIP_G2_USER@sbip-g2.d2.comp.nus.edu.sg:/users/trung/share/docker/docker_image_smartfuzz.tar

TOOLS_IDS=("ilf" "slither" "smartian" "sfuzz" "mythril" "confuzzius")
for TOOL_ID in ${TOOLS_IDS[@]}; do
    echo "- Preparing Docker image for: $TOOL_ID"
    docker save taquangtrung/$TOOL_ID > docker_image_${TOOL_ID}.tar

    echo "  Publishing Docker image to SBIP G2: $TOOL_ID"
    scp docker_image_${TOOL_ID}.tar   $SBIP_G2_USER@sbip-g2.d2.comp.nus.edu.sg:/users/trung/share/docker/docker_image_${TOOL_ID}.tar

done
