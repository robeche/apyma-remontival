"""
Configuración adicional para servir archivos media en PythonAnywhere
Añadir esto al archivo WSGI si es necesario
"""

import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.handlers.wsgi import WSGIHandler

# Configurar el módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings.production')

# Obtener la aplicación WSGI estándar
application = get_wsgi_application()

# Si necesitas servir archivos media manualmente (solo si Static files no funciona)
class MediaFilesHandler(WSGIHandler):
    """
    WSGI middleware que sirve archivos media para desarrollo.
    NO usar en producción real, solo para PythonAnywhere.
    """
    def __init__(self, application):
        self.application = application
        super().__init__()

    def __call__(self, environ, start_response):
        # Solo para rutas que empiecen con /media/
        if environ['PATH_INFO'].startswith('/media/'):
            return self.serve_media(environ, start_response)
        return self.application(environ, start_response)

    def serve_media(self, environ, start_response):
        from django.views.static import serve
        from django.http import Http404
        
        try:
            # Extraer la ruta del archivo
            path = environ['PATH_INFO'][len('/media/'):]
            
            # Usar la vista de Django para servir el archivo
            from django.conf import settings
            return serve(environ, start_response, path, settings.MEDIA_ROOT)
        except Http404:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'File not found']

# Solo usar el handler personalizado si es absolutamente necesario
# application = MediaFilesHandler(application)