"""
Django settings para techgear_web (frontend que consume la API FastAPI).

Pensado para correr en local y en Vercel:
- Sin base de datos: las sesiones viven en una cookie firmada (Vercel no permite escribir SQLite).
- Toda la configuracion sensible sale de variables de entorno.
"""

import os
from pathlib import Path

from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def _env_list(name):
    return [v.strip() for v in os.getenv(name, '').split(',') if v.strip()]


# Vercel define VERCEL=1 automaticamente. En local DEBUG es True salvo que lo cambies en .env
IS_VERCEL = bool(os.getenv('VERCEL'))
DEBUG = os.getenv('DEBUG', 'False' if IS_VERCEL else 'True').strip().lower() in ('1', 'true', 'yes')

SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'dev-only-insecure-key-do-not-use-in-production'
    else:
        raise ImproperlyConfigured(
            'Falta la variable de entorno SECRET_KEY. Definela en Vercel > Settings > Environment Variables.')

# Dominios permitidos. Extra: ALLOWED_HOSTS=midominio.com,www.midominio.com
ALLOWED_HOSTS = ['.vercel.app', 'localhost', '127.0.0.1'] + _env_list('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app'] + [
    o if o.startswith('http') else f'https://{o}' for o in _env_list('ALLOWED_HOSTS')]

# Vercel termina el HTTPS en su proxy; sin esto Django cree que es http y rechaza los POST (CSRF)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Application definition
INSTALLED_APPS = [
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'techgear_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'techgear_web.wsgi.application'

# Sin base de datos propia: los datos viven en MongoDB a traves de la API FastAPI.
DATABASES = {}

# La sesion (token JWT, nombre, rol) va en una cookie firmada, sin tabla en BD.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 60 * 60  # igual que el token JWT (60 min)
SESSION_COOKIE_HTTPONLY = True


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# Static files. Vercel detecta STATIC_ROOT, ejecuta collectstatic solo y sirve /static/ desde su CDN.
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Nombres con hash (techgear.abc123.css): permite cachear los estáticos un año sin que se queden viejos.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL de la API FastAPI (Render por defecto; en local: API_URL=http://127.0.0.1:8000)
API_URL = os.getenv('API_URL', 'https://fas-api2.onrender.com').rstrip('/')

# Los mensajes 'error' de Django usan la clase 'danger' de Bootstrap
MESSAGE_TAGS = {message_constants.ERROR: 'danger'}
