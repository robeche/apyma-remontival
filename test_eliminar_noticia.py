#!/usr/bin/env python
"""
Script para probar funcionalidad de eliminación de noticias
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings.development')
django.setup()

from usuarios.models import Noticia
from django.contrib.auth.models import User

def test_eliminar_noticia():
    """Prueba la funcionalidad de eliminación"""
    
    print("=== Test de Eliminación de Noticias ===\n")
    
    # 1. Verificar noticias existentes
    noticias = Noticia.objects.all()
    print("1. Noticias existentes:")
    for noticia in noticias:
        print(f"   ID: {noticia.id}, Título: {noticia.titulo}, Publicada: {noticia.publicada}")
    print()
    
    # 2. Verificar usuarios staff
    staff_users = User.objects.filter(is_staff=True)
    print("2. Usuarios staff:")
    for user in staff_users:
        print(f"   Username: {user.username}, Active: {user.is_active}, Staff: {user.is_staff}")
    print()
    
    # 3. Crear una noticia de prueba si no hay ninguna
    if not noticias.exists():
        print("3. Creando noticia de prueba...")
        noticia_test = Noticia.objects.create(
            titulo="Noticia de Prueba",
            resumen="Esta es una noticia de prueba para eliminar",
            contenido="Contenido de prueba para verificar la eliminación",
            publicada=True
        )
        print(f"   Noticia creada: ID {noticia_test.id}")
    else:
        print("3. Ya existen noticias, no se crea ninguna nueva")
    
    print("\n=== Fin del test ===")

if __name__ == "__main__":
    test_eliminar_noticia()