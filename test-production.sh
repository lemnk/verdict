#!/bin/bash

# Production deployment test script
set -e

echo "🧪 Testing VerdictVault production deployment..."

# Test frontend
echo "📱 Testing frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed: $FRONTEND_STATUS"
    exit 1
fi

# Test API
echo "🔌 Testing API..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed: $API_STATUS"
    exit 1
fi

# Test frontend page load
echo "🌐 Testing frontend page load..."
PAGE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$PAGE_STATUS" = "200" ]; then
    echo "✅ Frontend page load passed"
else
    echo "❌ Frontend page load failed: $PAGE_STATUS"
    exit 1
fi

# Test service health
echo "🏥 Testing service health..."
if docker-compose --profile prod ps | grep -q "unhealthy"; then
    echo "❌ Some services are unhealthy"
    docker-compose --profile prod ps
    exit 1
else
    echo "✅ All services are healthy"
fi

echo ""
echo "🎉 Production deployment test passed!"
echo "🌐 Frontend: http://localhost"
echo "🔌 API: http://localhost/api"
echo "📊 Health: http://localhost/health"