#!/bin/bash

echo "=== Checking if lib directory exists in container ==="
docker exec flightbrief-frontend ls -la /app/lib

echo ""
echo "=== Checking if files exist in container ==="
docker exec flightbrief-frontend ls -la /app/lib/api.ts
docker exec flightbrief-frontend ls -la /app/lib/utils.ts

echo ""
echo "=== Checking tsconfig paths ==="
docker exec flightbrief-frontend cat /app/tsconfig.json | grep -A 5 "paths"
