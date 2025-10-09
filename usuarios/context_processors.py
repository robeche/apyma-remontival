import time

def css_version(request):
    """
    Context processor para añadir una versión de CSS basada en timestamp
    """
    return {
        'css_version': str(int(time.time()))
    }