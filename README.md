# Santa's Draw - Secret Santa API

FastAPI-based RESTful API project for Secret Santa draw management.

## Features

- 🔐 User authentication and authorization
- 🎲 Draw creation and management
- 👥 Participant addition and removal
- 🎁 Automatic matching algorithm
- 📧 Email notifications
- 🔄 Versioned API (v1)

## Technologies

- **FastAPI** 0.120.0 - Modern web framework
- **Pydantic** 2.12.3 - Data validation
- **Python** 3.13
- **Uvicorn** - ASGI server
- **SQLAlchemy** 2.0.36 - ORM
- **PostgreSQL** - Database
- **Alembic** 1.14.0 - Database migrations

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd santas_draw

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# That's it! Application is running at http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Prerequisites

- Docker & Docker Compose

No Python, PostgreSQL, or other dependencies needed!

## Available Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View application logs only
docker-compose logs -f app

# View database logs only
docker-compose logs -f postgres

# Rebuild and start
docker-compose up -d --build

# Stop and remove volumes
docker-compose down -v
```

## Configuration

The application uses environment variables loaded from `.env` file. Key settings:

- `APP_NAME` - Application name
- `APP_VERSION` - Application version
- `DEBUG` - Debug mode (True/False)
- `API_VERSION` - API version
- `HOST` - Server host
- `PORT` - Server port
- `CORS_ORIGINS` - CORS allowed origins
- `DATABASE_URL` - PostgreSQL connection string
- `DATABASE_ECHO` - Log SQL queries (True/False)
- `DATABASE_POOL_SIZE` - Connection pool size
- `DATABASE_MAX_OVERFLOW` - Max overflow connections

## API Documentation

After running the application:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── main.py          # Main application
├── models/          # Database models
├── schemas/         # Pydantic schemas
├── api/
│   ├── deps.py      # Dependency injection
│   └── v1/          # API endpoints
├── config/          # Configuration
└── tasks/           # Background tasks
```

## License

AGPL v3 - See LICENSE file for details.
