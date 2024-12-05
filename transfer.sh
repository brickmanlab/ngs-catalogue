#!/bin/bash
# This script is used to build and transfer the ngs-catalogue
# into into cellyapp01fl where it gets deployed separately
set -e

VERSION=$(git rev-parse --short HEAD)
CELLY_PATH=/datasets/celly_brickman/ngs-catalogue

echo "Initializing database ..."
module load miniconda/latest && source activate ngs_catalogue
bin/initdb.py

echo "Build image: $VERSION ..."
podman build . -t brickmanlab/ngs-catalogue:$VERSION

echo "Removing and recreating CELLY_PATH"
rm -rf $CELLY_PATH
mkdir $CELLY_PATH

echo "Compressing image ..."
podman save \
    --output $CELLY_PATH/ngs-catalogue.tar \
    ngs-catalogue:$VERSION

echo "Copy 'db' folder"
cp -R db $CELLY_PATH/
# rsync -avzh db $CELLY_PATH/
