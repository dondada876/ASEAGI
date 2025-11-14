#!/bin/bash
# Build and push Vast.ai Docker image

set -e

# Load environment
if [ -f ../.env ]; then
    source ../.env
fi

DOCKER_USERNAME=${DOCKER_USERNAME:-"aseagi"}
DOCKER_IMAGE=${DOCKER_IMAGE:-"aseagi/document-processor"}
VERSION=${VERSION:-"latest"}

echo "🐳 Building Docker image: $DOCKER_IMAGE:$VERSION"

# Build image
docker build -t $DOCKER_IMAGE:$VERSION .

# Tag as latest
docker tag $DOCKER_IMAGE:$VERSION $DOCKER_IMAGE:latest

echo "📦 Pushing to Docker Hub..."

# Login to Docker Hub
docker login -u $DOCKER_USERNAME

# Push both tags
docker push $DOCKER_IMAGE:$VERSION
docker push $DOCKER_IMAGE:latest

echo "✅ Image pushed successfully!"
echo "🚀 Use this image on Vast.ai: $DOCKER_IMAGE:latest"
