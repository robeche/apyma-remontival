#!/usr/bin/env python
"""
Script de diagnóstico para problemas de media files
"""

import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings.development')
django.setup()

from usuarios.models import Noticia

def diagnosticar_media():
    """Diagnóstica problemas con archivos media"""
    
    print("=== Diagnóstico de Media Files ===\n")
    
    # 1. Verificar configuración
    print("1. Configuración de Django:")
    print(f"   MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'NO CONFIGURADO')}")
    print(f"   MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'NO CONFIGURADO')}")
    print(f"   DEBUG: {getattr(settings, 'DEBUG', 'NO CONFIGURADO')}")
    print()
    
    # 2. Verificar directorio media
    media_root = getattr(settings, 'MEDIA_ROOT', '')
    if media_root:
        print("2. Directorio media:")
        print(f"   Ruta: {media_root}")
        print(f"   Existe: {os.path.exists(media_root)}")
        if os.path.exists(media_root):
            print(f"   Permisos: {oct(os.stat(media_root).st_mode)[-3:]}")
        print()
        
        # Listar contenido del directorio media
        if os.path.exists(media_root):
            print("   Contenido del directorio media:")
            for root, dirs, files in os.walk(media_root):
                level = root.replace(media_root, '').count(os.sep)
                indent = ' ' * 4 * (level + 1)
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 4 * (level + 2)
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    print(f"{subindent}{file} ({file_size} bytes)")
        print()
    
    # 3. Verificar noticias con imagen
    print("3. Noticias con imagen:")
    noticias_con_imagen = Noticia.objects.exclude(imagen='')
    
    if noticias_con_imagen.exists():
        for noticia in noticias_con_imagen:
            print(f"   Noticia: {noticia.titulo}")
            print(f"   Campo imagen: {noticia.imagen}")
            if noticia.imagen:
                print(f"   Ruta completa: {noticia.imagen.path if hasattr(noticia.imagen, 'path') else 'N/A'}")
                print(f"   URL: {noticia.imagen.url if hasattr(noticia.imagen, 'url') else 'N/A'}")
                
                # Verificar si el archivo existe físicamente
                if hasattr(noticia.imagen, 'path'):
                    existe = os.path.exists(noticia.imagen.path)
                    print(f"   Archivo existe: {existe}")
                    if existe:
                        size = os.path.getsize(noticia.imagen.path)
                        print(f"   Tamaño: {size} bytes")
            print()
    else:
        print("   No hay noticias con imagen")
        print()
    
    # 4. Verificar todas las noticias
    print("4. Todas las noticias:")
    todas_noticias = Noticia.objects.all()
    for noticia in todas_noticias:
        tiene_imagen = bool(noticia.imagen)
        print(f"   {noticia.titulo} - Imagen: {'✓' if tiene_imagen else '✗'}")
    
    print("\n=== Fin del diagnóstico ===")

if __name__ == "__main__":
    diagnosticar_media()