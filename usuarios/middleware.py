from django.conf import settings
from django.http import HttpResponsePermanentRedirect

class DomainRedirectMiddleware:
    """
    Middleware para redirigir automáticamente al dominio principal
    donde funcionan las sesiones y cookies
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo redirigir en producción
        if hasattr(settings, 'PRIMARY_DOMAIN'):
            host = request.get_host()
            primary_domain = settings.PRIMARY_DOMAIN
            
            # Si no estamos en el dominio principal, redirigir
            if host != primary_domain and not host.startswith('127.0.0.1') and not host.startswith('localhost'):
                protocol = 'https' if request.is_secure() else 'http'
                redirect_url = f"{protocol}://{primary_domain}{request.get_full_path()}"
                return HttpResponsePermanentRedirect(redirect_url)

        response = self.get_response(request)
        return response