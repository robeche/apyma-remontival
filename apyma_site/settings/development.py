"""
Configuración de desarrollo - Apyma Remontival
"""

from .base import *
from decouple import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default="django-insecure-3l_-#m55wi-naqwxq9*^rpx&_v_zf8=9nz34krep70-8v^gfda")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database para desarrollo
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Email Configuration para desarrollo
# Para desarrollo, usa el backend de consola para ver emails en terminal
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Si necesitas probar SMTP real, configura variables de entorno
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# DEFAULT_FROM_EMAIL = f'Apyma Remontival <{config("EMAIL_HOST_USER", default="")}'>'

# Google reCAPTCHA Configuration - CLAVES DE PRUEBA (públicas de Google)
# Estas claves de prueba funcionan en cualquier dominio para testing
RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY', default='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY', default='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')

# Para desarrollo, también puedes usar el backend de consola para ver emails en terminal
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'