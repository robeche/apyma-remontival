"""
URL configuration for apyma_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from usuarios.views import simple_set_language

# Personalizar el admin site
admin.site.site_header = 'Administración APYMA Remontival'
admin.site.site_title = 'APYMA Admin'
admin.site.index_title = 'Panel de Administración'

urlpatterns = [
    path("admin/", admin.site.urls),  # Admin normal de Django
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', simple_set_language, name='simple_set_language'),
]

urlpatterns += i18n_patterns(
    path("", include("usuarios.urls")),
)

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
