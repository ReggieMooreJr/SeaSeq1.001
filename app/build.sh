#!/bin/bash

# File to store the current version
VERSION_FILE="version.txt"

# Read the current version from the file (default to 1.0 if the file doesn't exist)
if [ ! -f "$VERSION_FILE" ]; then
  echo "1.0" > "$VERSION_FILE"
fi
VERSION=$(cat "$VERSION_FILE")

# Use lowercase image and container names (Docker requirement)
IMAGE_NAME="seaseq_image_v${VERSION}"
CONTAINER_NAME="seaseq_container_v${VERSION}"

# Build the Docker image with the versioned tag
docker build -t $IMAGE_NAME .

# Increment the version (e.g., 1.0 -> 1.1)
NEW_VERSION=$(echo "$VERSION + 0.1" | bc)
echo "$NEW_VERSION" > "$VERSION_FILE"

# Run the container with the versioned name
docker run --name $CONTAINER_NAME -d -p 8000:8000 $IMAGE_NAME

# Output the details
echo "Built and ran container:"
echo "  Image: $IMAGE_NAME"
echo "  Container: $CONTAINER_NAME"
