from santasdraw.settings.base import *

# Development settings
DEBUG = True

# Secret key for development (should be different from production)
SECRET_KEY = 'django-insecure-hv70-g(368l@ls_^$h%g2k=b7om59%@x3hez(g24qo^u=0d=3g'

# Allow all hosts for development
ALLOWED_HOSTS = ['*']

# Database configuration for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
