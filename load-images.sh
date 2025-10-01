#!/bin/bash

# A script to build and load local microservice images into KIND.

set -e # Exit immediately if a command fails.

echo "📦 Building and loading service images into the cluster..."

# Array of your service directories
SERVICES=("api" "processing" "notification" "analytics")

for SERVICE in "${SERVICES[@]}"; do
  IMAGE_NAME="${SERVICE}-service:latest"
  
  echo "--- Building $IMAGE_NAME from ./$SERVICE directory ---"
  docker build -t "$IMAGE_NAME" -f "./$SERVICE/Dockerfile" .
  
  echo "--- Loading $IMAGE_NAME into KIND ---"
  kind load docker-image "$IMAGE_NAME"
done

echo "🎉 All images loaded successfully!"