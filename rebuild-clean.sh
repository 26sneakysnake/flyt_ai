#!/bin/bash

echo "=== Cleaning up Docker completely ==="

# Stop all containers
echo "Stopping containers..."
docker-compose down -v

# Remove the specific images
echo "Removing frontend image..."
docker rmi flyt_ai-frontend 2>/dev/null || true

echo "Removing backend image..."
docker rmi flyt_ai-backend 2>/dev/null || true

# Remove build cache
echo "Pruning build cache..."
docker builder prune -f

echo ""
echo "=== Rebuilding from scratch ==="
docker-compose build --no-cache

echo ""
echo "=== Starting services ==="
docker-compose up
