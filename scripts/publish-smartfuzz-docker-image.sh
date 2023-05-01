#!/usr/bin/env sh

echo "Preparing SmartFuzz Docker image..."
docker tag smartbench/smartfuzz taquangtrung/smartfuzz
docker save taquangtrung/smartfuzz > docker_image_smartfuzz.tar

echo -n "Enter your username in SBIP G2 to publish Smartfuzz Docker image: "
read SBIP_G2_USER

echo "Publishing Smartfuzz Docker image to SBIP G2..."
scp docker_image_smartfuzz.tar  $SBIP_G2_USER@sbip-g2.d2.comp.nus.edu.sg:/users/trung/share/docker/docker_image_smartfuzz.tar
