#!/bin/bash

# Restart script for FlightBrief AI

echo "Stopping containers..."
docker-compose down

echo "Removing Next.js cache..."
rm -rf frontend/.next
rm -rf frontend/node_modules/.cache

echo "Starting containers..."
docker-compose up --build

echo "Application should be ready at http://localhost:3000"
