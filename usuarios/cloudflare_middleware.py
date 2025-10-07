from django.utils.deprecation import MiddlewareMixin

class CloudflareHostMiddleware(MiddlewareMixin):
    """
    Middleware para hacer que Django use X-Original-Host como si fuera X-Forwarded-Host
    Específico para el setup de Cloudflare Worker actual
    """
    def process_request(self, request):
        # Si tenemos X-Original-Host pero no X-Forwarded-Host, copiar el valor
        if 'HTTP_X_ORIGINAL_HOST' in request.META and 'HTTP_X_FORWARDED_HOST' not in request.META:
            request.META['HTTP_X_FORWARDED_HOST'] = request.META['HTTP_X_ORIGINAL_HOST']
            request.META['HTTP_X_FORWARDED_PROTO'] = 'https'