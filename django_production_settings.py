# Configuration Django pour la production AUTO REPUBLIC RDC
# À ajouter dans votre fichier car/settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuration pour la production
DEBUG = False

# Autoriser votre IP et domaines
ALLOWED_HOSTS = [
    '77.37.51.63',  # Votre IP VPS
    'localhost',
    '127.0.0.1',
    'votre-domaine.com',  # Remplacez par votre domaine
    'www.votre-domaine.com',
]

# Configuration CSRF pour votre IP
CSRF_TRUSTED_ORIGINS = [
    'http://77.37.51.63',
    'https://77.37.51.63',
    'http://votre-domaine.com',  # Remplacez par votre domaine
    'https://votre-domaine.com',
]

# Configuration des fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuration des fichiers média
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuration des répertoires statiques supplémentaires
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'home', 'static'),
]

# Configuration pour la collecte des fichiers statiques
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configuration de sécurité pour la production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuration des sessions (décommentez si vous utilisez HTTPS)
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Configuration de la base de données (exemple avec SQLite pour commencer)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuration du cache (optionnel)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }

# Configuration des logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/www/auto/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
