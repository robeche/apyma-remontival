import os
import sys

# Añadir el directorio del proyecto al path
path = '/home/yourusername/ApymaRemontival'  # Cambiar 'yourusername' por tu usuario
if path not in sys.path:
    sys.path.append(path)

# Configurar Django settings para producción
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings.production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()