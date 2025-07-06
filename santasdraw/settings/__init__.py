from decouple import config

from santasdraw.settings.base import *

# Get environment setting with default fallback to 'local'
ENVIRONMENT = config('ENVIRONMENT', default='local')

if ENVIRONMENT == 'production':
    from santasdraw.settings.production import *
elif ENVIRONMENT == 'staging':
    from santasdraw.settings.staging import *
else:
    from santasdraw.settings.local import *
