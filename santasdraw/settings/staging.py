import os
from decouple import config, Csv
from santasdraw.settings.base import *

# Staging settings (similar to production but with less strict security)
DEBUG = config('DEBUG', default=False, cast=bool)

# Secret key from environment variable
SECRET_KEY = config('SECRET_KEY')

# Allowed hosts from environment variable
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# CORS settings for staging
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=False, cast=bool)

# Email configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Static files configuration
STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))

# Media files configuration
MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
MEDIA_URL = config('MEDIA_URL', default='/media/')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='DEBUG'),
        },
        'santasdraw': {
            'handlers': ['console'],
            'level': config('APP_LOG_LEVEL', default='DEBUG'),
        },
    },
}