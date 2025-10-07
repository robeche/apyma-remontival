from django.conf import settings
from django.http import HttpResponsePermanentRedirect

class ForceWorkingDomainMiddleware:
    """
    Middleware para redirigir todo al dominio que funciona
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo en producción
        if not settings.DEBUG:
            host = request.get_host()
            working_domain = 'robeche.pythonanywhere.com'
            
            # Si no estamos en el dominio que funciona, redirigir
            if host != working_domain:
                protocol = 'https' if request.is_secure() else 'http'
                redirect_url = f"{protocol}://{working_domain}{request.get_full_path()}"
                return HttpResponsePermanentRedirect(redirect_url)

        response = self.get_response(request)
        return response