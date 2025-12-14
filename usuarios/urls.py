from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('area-socios/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),  # Sin success_url
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    # path('dashboard/', views.dashboard, name='dashboard'),  # Temporalmente deshabilitado
    # path('contacto/', views.contacto, name='contacto'),  # Eliminado - ahora se usa modal
    path('comedor/', views.comedor, name='comedor'),
    path('comedor/gestionar/', views.gestionar_menus, name='gestionar_menus'),
    path('comedor/pdf/<str:filename>/', views.serve_pdf, name='serve_pdf'),
    path('comedor/gestionar/', views.gestionar_menus, name='gestionar_menus'),
    path('extraescolares/', views.extraescolares, name='extraescolares'),
    path('aula-madrugadores/', views.aula_madrugadores, name='aula_madrugadores'),
    path('actividades/', views.actividades, name='actividades'),
    path('concurso-navideno/', views.concurso_navideno, name='concurso_navideno'),
    path('actividades/crear/', views.crear_actividad, name='crear_actividad'),
    path('actividades/<int:actividad_id>/', views.detalle_actividad, name='detalle_actividad'),
    path('actividades/<int:actividad_id>/editar/', views.actualizar_actividad, name='actualizar_actividad'),
    path('actividades/<int:actividad_id>/eliminar/', views.eliminar_actividad, name='eliminar_actividad'),
    path('noticias/', views.noticias_lista, name='noticias_lista'),
    # path('noticias/<slug:slug>/', views.noticia_detalle, name='noticia_detalle'),  # No necesario con modal
    path('noticias/crear/', views.crear_noticia, name='crear_noticia'),
    path('noticias/<int:noticia_id>/editar/', views.editar_noticia, name='editar_noticia'),
    path('noticias/<int:noticia_id>/eliminar/', views.eliminar_noticia, name='eliminar_noticia'),
    path('noticias/<int:noticia_id>/obtener/', views.obtener_noticia, name='obtener_noticia'),
    path('noticia/<int:noticia_id>/', views.obtener_noticia_publica, name='obtener_noticia_publica'),
    path('debug-redirect/', views.debug_redirect, name='debug_redirect'),
    path('debug-headers/', views.debug_headers_cookies, name='debug_headers'),  # TEMPORAL DEBUG
    path('test-session/', views.test_session, name='test_session'),  # TEMPORAL SESSION TEST
    path('debug-login/', views.debug_login, name='debug_login'),  # TEMPORAL LOGIN DEBUG
    # path('debug-admin-user/', views.debug_admin_user, name='debug_admin_user'),  # TEMPORAL - DESACTIVADO
]
