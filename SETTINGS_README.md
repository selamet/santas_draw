# Django Settings Configuration

This project uses environment-based Django settings for better security and deployment flexibility.

## Settings Structure

```
santasdraw/settings/
├── __init__.py          # Auto-detects environment and imports appropriate settings
├── base.py              # Common settings shared across all environments
├── local.py             # Development settings
├── staging.py           # Staging environment settings
└── production.py        # Production settings with security configurations
```

## Environment Configuration

The settings are automatically selected based on the `ENVIRONMENT` environment variable:

- `ENVIRONMENT=local` (default) - Uses `local.py` for development
- `ENVIRONMENT=staging` - Uses `staging.py` for staging environment
- `ENVIRONMENT=production` - Uses `production.py` for production deployment

## Quick Start

### Local Development

For local development, no environment variables are required. Simply run:

```bash
python manage.py runserver
```

### Staging/Production

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the environment variables in `.env`:
   ```bash
   ENVIRONMENT=production
   SECRET_KEY=your-production-secret-key
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

3. Run your Django application:
   ```bash
   python manage.py collectstatic
   python manage.py migrate
   python manage.py runserver
   ```

## Environment Variables

### Required for Production/Staging

- `SECRET_KEY` - Django secret key for cryptographic signing
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

### Optional Environment Variables

- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DEBUG` - Enable debug mode (default: False for production/staging)
- `STATIC_ROOT` - Static files root path
- `MEDIA_ROOT` - Media files root path
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins
- `DJANGO_LOG_LEVEL` - Django logging level (default: INFO)
- `APP_LOG_LEVEL` - Application logging level (default: INFO)

## Security Features

### Production Settings Include:

- `DEBUG = False` - Disables debug mode
- SSL/HTTPS enforcement with security headers
- Secure cookie settings
- CORS configuration
- Comprehensive logging
- PostgreSQL database configuration

### Development Settings Include:

- `DEBUG = True` - Enables debug mode
- SQLite database for easy setup
- Console email backend
- Permissive CORS settings
- Detailed error reporting

## Database Configuration

- **Local**: SQLite database (`db.sqlite3`)
- **Staging/Production**: PostgreSQL database (requires environment variables)

## Static and Media Files

- **Local**: Served by Django development server
- **Production**: Configured for static file collection and serving

## Testing Different Environments

You can test different environments by setting the `ENVIRONMENT` variable:

```bash
# Test local environment
ENVIRONMENT=local python manage.py check

# Test staging environment
ENVIRONMENT=staging SECRET_KEY=test DB_NAME=test DB_USER=test DB_PASSWORD=test ALLOWED_HOSTS=localhost python manage.py check

# Test production environment
ENVIRONMENT=production SECRET_KEY=test DB_NAME=test DB_USER=test DB_PASSWORD=test ALLOWED_HOSTS=localhost python manage.py check --deploy
```

## Security Best Practices

1. **Never commit sensitive data** - Use environment variables for secrets
2. **Use strong SECRET_KEY** - Generate a long, random secret key for production
3. **Configure ALLOWED_HOSTS** - Restrict to your actual domain names
4. **Enable HTTPS** - Use SSL/TLS in production
5. **Regular updates** - Keep dependencies updated
6. **Database security** - Use strong database credentials and restrict access