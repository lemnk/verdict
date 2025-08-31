# VerdictVault

AI-powered legal precedent extractor built with FastAPI.

## Features

- Document upload and processing
- Legal precedent extraction
- Semantic search using RAG
- User authentication
- PostgreSQL storage with Redis caching

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+

### Development Setup

1. Install dependencies:
```bash
make install
```

2. Start services:
```bash
make up
```

3. Run development server:
```bash
make dev
```

### Production Setup

1. Build and start services:
```bash
make build
make up
```

## API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/upload/document` - Upload legal document
- `POST /api/search/precedents` - Search legal precedents

## Project Structure

```
app/
├── main.py          # FastAPI entry point
├── routers/         # API route handlers
├── models/          # Pydantic models
├── db/             # Database models and connection
└── utils/          # Utility functions
```

## Commands

- `make install` - Install Python dependencies
- `make dev` - Run development server
- `make up` - Start Docker services
- `make down` - Stop Docker services
- `make test` - Run tests
- `make clean` - Clean up Docker resources