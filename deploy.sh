#!/bin/bash

# Production deployment script for VerdictVault
set -e

echo "🚀 Starting VerdictVault production deployment..."

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "❌ .env.production file not found. Please create it from .env.production.example"
    exit 1
fi

# Copy production environment
echo "📋 Setting up production environment..."
cp .env.production .env

# Build frontend
echo "🔨 Building frontend for production..."
cd frontend
npm ci --only=production
npm run build
cd ..

# Start production services
echo "🐳 Starting production Docker services..."
docker-compose --profile prod up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
if docker-compose --profile prod ps | grep -q "unhealthy"; then
    echo "❌ Some services are unhealthy. Check logs with: docker-compose logs"
    exit 1
fi

echo "✅ Production deployment complete!"
echo "🌐 Frontend available at: http://localhost"
echo "🔌 API available at: http://localhost/api"
echo ""
echo "📊 View logs: docker-compose --profile prod logs -f"
echo "🛑 Stop services: docker-compose --profile prod down"