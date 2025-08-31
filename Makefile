.PHONY: install test test-parse test-rag dev dev-frontend build build-frontend up up-prod down clean logs migrate migration migrate-role

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

# Frontend development server
dev-frontend:
	cd frontend && npm run dev

# Build Docker image
build:
	docker-compose build

# Build frontend for production
build-frontend:
	cd frontend && npm run build

# Start development services
up:
	docker-compose --profile dev up -d

# Start production services
up-prod:
	docker-compose --profile prod up -d

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

# Add role column to users table
migrate-role:
	python migrate_add_role.py

# Parse document (example usage)
parse-doc:
	@echo "Usage: curl -X POST 'http://localhost:8000/api/parse/{doc_id}' -H 'Authorization: Bearer {token}'"

# Ask legal question (example usage)
ask-question:
	@echo "Usage: curl -X POST 'http://localhost:8000/api/rag/ask' -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{\"query\": \"What is contract law?\"}'"

# Production deployment
deploy: build-frontend up-prod
	@echo "Production deployment complete. Frontend available at http://localhost"