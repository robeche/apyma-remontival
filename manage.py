#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Detectar si estamos en PythonAnywhere (producción) o desarrollo local
    if 'pythonanywhere.com' in os.environ.get('SERVER_NAME', '') or \
       os.environ.get('PYTHONANYWHERE_DOMAIN'):
        # Estamos en PythonAnywhere (producción)
        print("Cargando configuración de producción...")
        default_settings = "apyma_site.settings.production"
    else:
        # Estamos en desarrollo local
        print("Cargando configuración de desarrollo...")
        default_settings = "apyma_site.settings.development"
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
