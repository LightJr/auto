# Configuration pour les fichiers statiques Django
# À ajouter dans votre fichier car/settings.py

# Configuration pour la production
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuration des fichiers statiques pour la production
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

# Configuration pour la production
DEBUG = False
ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com', '127.0.0.1', 'localhost']

# Configuration de sécurité pour la production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configuration des sessions
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configuration de la base de données (exemple avec PostgreSQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'auto_republic_db',
#         'USER': 'votre_utilisateur_db',
#         'PASSWORD': 'votre_mot_de_passe_db',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Configuration du cache (optionnel)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }
