#!/usr/bin/env sh

echo "Preparing Docker image..."
docker tag smartbench/smartfuzz taquangtrung/smartfuzz
docker save taquangtrung/smartfuzz > docker_image_smartfuzz.tar

echo "Publishing Smartfuzz Docker image to SBIP G2..."
scp docker_image_smartfuzz.tar  trung@sbip-g2.d2.comp.nus.edu.sg:/users/trung/share/docker/docker_image_smartfuzz.tar
