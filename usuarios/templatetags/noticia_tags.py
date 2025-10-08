from django import template
from django.utils.translation import get_language

register = template.Library()

@register.filter
def get_localized_titulo(noticia, language=None):
    """Obtiene el título localizado de una noticia"""
    if language is None:
        language = get_language()
    return noticia.get_titulo_localized(language)

@register.filter
def get_localized_resumen(noticia, language=None):
    """Obtiene el resumen localizado de una noticia"""
    if language is None:
        language = get_language()
    return noticia.get_resumen_localized(language)

@register.filter
def get_localized_contenido(noticia, language=None):
    """Obtiene el contenido localizado de una noticia"""
    if language is None:
        language = get_language()
    return noticia.get_contenido_localized(language)