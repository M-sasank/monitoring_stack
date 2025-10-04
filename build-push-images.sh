#!/bin/bash

# A script to build and load local microservice images into KIND.

set -e # Exit immediately if a command fails.

echo "📦 Building images..."

# Array of your service directories
SERVICES=("api" "processing" "notification" "analytics")

PROJECT_ID="devops-sm"
REPO_NAME="kubernetes-practice"
REGION_REF="asia-south1-docker.pkg.dev"
REGISTRY="${REGION_REF}/${PROJECT_ID}/${REPO_NAME}"

echo "--- Configuring docker for registry ---"
return=$(gcloud auth configure-docker ${REGION_REF})
if [ $? -ne 0 ]; then
  echo "--- Error configuring docker for registry ---"
  exit 1
fi
# extract current latest tag
for SERVICE in "${SERVICES[@]}"; do
  IMAGE_NAME="${SERVICE}-service:latest"
  
  echo "--- Building $IMAGE_NAME from ./$SERVICE directory ---"
  docker build -t "$IMAGE_NAME" -f "./$SERVICE/Dockerfile" .
  
  echo "--- Pushing $IMAGE_NAME into registry ---"
  REPO_IMAGE_NAME="${REGISTRY}/${SERVICE}-service:v1.0.0"
  echo "--- Tagging $IMAGE_NAME into $REPO_IMAGE_NAME ---"
  docker tag "$IMAGE_NAME" "${REPO_IMAGE_NAME}"
  echo "--- Pushing $REPO_IMAGE_NAME into registry ---"
  docker push "${REPO_IMAGE_NAME}"
done

echo " All images built and pushed successfully!"