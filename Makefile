.PHONY: install test test-parse test-rag dev build up down clean logs migrate migration

# Install dependencies
install:
	pip install -r requirements.txt

# Run all tests
test:
	python -m pytest tests/ -v

# Run parse-specific tests
test-parse:
	python -m pytest tests/test_parse.py -v

# Run RAG-specific tests
test-rag:
	python -m pytest tests/test_rag.py -v

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

# Parse document (example usage)
parse-doc:
	@echo "Usage: curl -X POST 'http://localhost:8000/api/parse/{doc_id}' -H 'Authorization: Bearer {token}'"

# Ask legal question (example usage)
ask-question:
	@echo "Usage: curl -X POST 'http://localhost:8000/api/rag/ask' -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{\"query\": \"What is contract law?\"}'"