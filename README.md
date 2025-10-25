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

## Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env file with your database settings
# Update DATABASE_URL if needed

# Run database migrations (once PostgreSQL is running)
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## Database Setup

The application uses PostgreSQL. Make sure PostgreSQL is installed and running:

```bash
# Create database
createdb santas_draw

# Or use psql
psql -U postgres
CREATE DATABASE santas_draw;
```

Update `.env` file with your database credentials:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/santas_draw
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
