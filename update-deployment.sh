#!bin/bash

# update all services
kubectl apply -f k8s/notification-service/deployment.yaml
kubectl apply -f k8s/processing-service/deployment.yaml
kubectl apply -f k8s/analytics-service/deployment.yaml
kubectl apply -f k8s/api-service/deployment.yaml
