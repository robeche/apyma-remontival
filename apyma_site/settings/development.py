"""
Configuración de desarrollo - Apyma Remontival
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-3l_-#m55wi-naqwxq9*^rpx&_v_zf8=9nz34krep70-8v^gfda"

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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apymaremontivaladm@gmail.com'  # Nueva cuenta de la Apyma
EMAIL_HOST_PASSWORD = 'sqwx lhjv amix nxoz'  # Contraseña de aplicación
DEFAULT_FROM_EMAIL = 'Apyma Remontival <apymaremontivaladm@gmail.com>'

# Google reCAPTCHA Configuration - CLAVES DE PRUEBA
# Estas claves funcionan en cualquier dominio para testing
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'  # Test key
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'  # Test key

# Para desarrollo, también puedes usar el backend de consola para ver emails en terminal
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'