.PHONY: install test dev build up down clean logs

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests/ -v

# Development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Build Docker image
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Database migrations
migrate:
	alembic upgrade head

# Create migration
migration:
	alembic revision --autogenerate -m "$(message)"