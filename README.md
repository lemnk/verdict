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
make up-prod
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

## Deployment

### Local Production Deployment

1. **Build frontend for production:**
```bash
make build-frontend
```

2. **Start production services:**
```bash
make up-prod
```

3. **Access the application:**
   - Frontend: http://localhost
   - API: http://localhost/api

### AWS EC2 Deployment

1. **Launch EC2 instance:**
   - Ubuntu 22.04 LTS
   - t3.medium or larger
   - Security group: HTTP (80), HTTPS (443), SSH (22)

2. **Install Docker:**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

3. **Clone and deploy:**
```bash
git clone <repository-url>
cd verdictvault
./deploy.sh
```

4. **Set up environment:**
```bash
cp .env.production .env
# Edit .env with your production values
```

### Database Configuration

#### Local PostgreSQL
- Default: `postgresql://verdictvault:password@localhost:5432/verdictvault`
- Update `DATABASE_URL` in `.env` if needed

#### AWS RDS
- Launch RDS PostgreSQL instance
- Update `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/verdictvault
```

### File Storage

#### Local Storage (Default)
- PDFs stored in `./uploads/` directory
- Mounted to Docker container

#### AWS S3 (Recommended for Production)
- Create S3 bucket for document storage
- Update upload logic to use S3 instead of local filesystem
- Configure S3 credentials in `.env`

### Environment Variables

Create `.env.production` with:
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
OPENAI_API_KEY=your_key_here
JWT_SECRET=your_super_secret_key
```

### Production Commands

```bash
# Build and deploy
make deploy

# View logs
docker-compose --profile prod logs -f

# Stop production services
docker-compose --profile prod down

# Restart services
docker-compose --profile prod restart
```

### Health Checks

All services include health checks:
- **API**: `GET /api/health`
- **Web**: `GET /health`
- **Database**: PostgreSQL readiness check
- **Redis**: Ping command

### Monitoring

- **Logs**: `docker-compose --profile prod logs -f`
- **Status**: `docker-compose --profile prod ps`
- **Resources**: `docker stats`

### Scaling

- **Horizontal**: Add more API containers behind nginx
- **Vertical**: Increase EC2 instance size
- **Database**: Use RDS with read replicas
- **Cache**: Redis cluster for high availability

## Security Considerations

- Change default passwords
- Use strong JWT secrets
- Enable HTTPS in production
- Restrict database access
- Regular security updates
- Monitor access logs

## Troubleshooting

### Common Issues

1. **Port conflicts:**
```bash
sudo lsof -i :80
sudo lsof -i :8000
```

2. **Permission issues:**
```bash
sudo chown -R $USER:$USER .
```

3. **Database connection:**
```bash
docker-compose logs db
```

4. **Frontend build errors:**
```bash
cd frontend && npm ci && npm run build
```

### Logs and Debugging

```bash
# View all logs
docker-compose --profile prod logs

# View specific service logs
docker-compose --profile prod logs api

# Follow logs in real-time
docker-compose --profile prod logs -f
```

## License

MIT