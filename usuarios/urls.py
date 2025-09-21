from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('area-socios/', auth_views.LoginView.as_view(template_name='usuarios/login.html', success_url=reverse_lazy('dashboard')), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contacto/', views.contacto, name='contacto'),
]
