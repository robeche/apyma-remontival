from django.conf import settings
from django.http import HttpResponsePermanentRedirect

class OriginalHostMiddleware:
    """
    Middleware para usar X-Original-Host del Cloudflare Worker
    como si fuera X-Forwarded-Host
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si viene X-Original-Host, copiarlo a X-Forwarded-Host
        if 'HTTP_X_ORIGINAL_HOST' in request.META:
            original_host = request.META['HTTP_X_ORIGINAL_HOST']
            request.META['HTTP_X_FORWARDED_HOST'] = original_host
            request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
            
        response = self.get_response(request)
        return response

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