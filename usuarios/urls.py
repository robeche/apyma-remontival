from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('area-socios/', auth_views.LoginView.as_view(template_name='usuarios/login.html', success_url=reverse_lazy('dashboard')), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contacto/', views.contacto, name='contacto'),
    path('actividades/', views.actividades, name='actividades'),
    path('actividades/crear/', views.crear_actividad, name='crear_actividad'),
    path('actividades/<int:actividad_id>/', views.detalle_actividad, name='detalle_actividad'),
    path('actividades/<int:actividad_id>/editar/', views.actualizar_actividad, name='actualizar_actividad'),
    path('actividades/<int:actividad_id>/eliminar/', views.eliminar_actividad, name='eliminar_actividad'),
]
