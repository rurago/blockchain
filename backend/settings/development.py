from .base import *

DEBUG = True

# Configuración específica para desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Para desarrollo, permitir todos los hosts
ALLOWED_HOSTS = ['*']