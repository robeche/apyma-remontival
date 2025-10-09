"""
Configuración de producción - Apyma Remontival
"""

import os
from decouple import config
from .base import *

# Añadir whitenoise para archivos estáticos
MIDDLEWARE = [
    "usuarios.cloudflare_middleware.CloudflareHostMiddleware",  # PRIMERO - antes que SecurityMiddleware
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Añadido para producción
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'apymaremontival.pythonanywhere.com',
    'www.apymaremontival.com',
    'apymaremontival.com',
    'robeche.pythonanywhere.com',
    '*.apymaremontival.com',  # Comodín para subdominios
]

# CSRF Trusted Origins (necesario para Django 4.0+)
CSRF_TRUSTED_ORIGINS = [
    'https://apymaremontival.pythonanywhere.com',
    'https://www.apymaremontival.com',
    'https://apymaremontival.com',
    'https://apyma-remontival.org',
    'https://www.apyma-remontival.org',
    'http://apymaremontival.pythonanywhere.com',  # Para desarrollo si no hay SSL
]

# Configuración adicional de CSRF para Cloudflare
CSRF_COOKIE_HTTPONLY = False  # Permitir acceso desde JavaScript
CSRF_USE_SESSIONS = False  # Usar cookies en lugar de sesiones para CSRF
CSRF_COOKIE_AGE = 31449600  # 1 año

# Database para producción (PostgreSQL recomendado)
# Configuración de PostgreSQL si están disponibles las variables
DB_NAME = config('DB_NAME', default='')
DB_USER = config('DB_USER', default='')
DB_PASSWORD = config('DB_PASSWORD', default='')

if DB_NAME and DB_USER and DB_PASSWORD:
    # Usar PostgreSQL si están configuradas las variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    # Fallback a SQLite si no hay configuración de PostgreSQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Email Configuration para producción (usando variables de entorno)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f'Apyma Remontival <{config("EMAIL_HOST_USER")}>'

# Configuración de seguridad para producción
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Permitir iframes del mismo dominio para PDFs

# HTTPS settings para Cloudflare
SECURE_SSL_REDIRECT = False  # Cloudflare maneja esto
SESSION_COOKIE_SECURE = True  # Reactivar cookies seguras
CSRF_COOKIE_SECURE = True     # Reactivar CSRF seguras

# Configuración específica para Cloudflare
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Como Cloudflare Worker envía X-Original-Host en lugar de X-Forwarded-Host
# Necesitamos un middleware personalizado o forzar el uso
FORCE_HOST_FROM_X_ORIGINAL = True

# Configuración de cookies para que funcionen con Cloudflare
SESSION_COOKIE_DOMAIN = None  # Usar el dominio de la request actual
CSRF_COOKIE_DOMAIN = None     # Usar el dominio de la request actual

SESSION_COOKIE_NAME = 'apyma_sessionid'
CSRF_COOKIE_NAME = 'apyma_csrftoken'

# Para asegurar compatibilidad cross-domain
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True  # Seguridad adicional

# Static files para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración de media files para producción
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración adicional de seguridad
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging para producción
import os
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configuración de WhiteNoise para evitar cache excesivo
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Configuración de cache para archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Headers de cache para archivos estáticos
WHITENOISE_MAX_AGE = 0  # Deshabilitar cache por completo (solo para debug)