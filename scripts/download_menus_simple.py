#!/usr/bin/env python
"""
Script simple para descargar los menús del comedor
"""

import os
import requests
from datetime import datetime

def download_menus():
    """Descarga los menús del comedor"""
    
    # Directorio de destino
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    media_dir = os.path.join(base_dir, 'media', 'comedor')
    
    # Crear directorio si no existe
    os.makedirs(media_dir, exist_ok=True)
    
    # URLs de los menús
    menu_urls = {
        'menu_septiembre_castellano': 'https://www.elgustodecrecer.es/Users/Menus/Archivos/20250908_134856_BASAL%20SEPTIEMBRE%20in.pdf',
        'menu_septiembre_euskera': 'https://www.elgustodecrecer.es/Users/Menus/Archivos/20250908_135206_BASALA%20IRAILA%20in.pdf'
    }
    
    print("=== Descargador de Menús del Comedor ===")
    print(f"Directorio de destino: {media_dir}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success_count = 0
    
    for filename, url in menu_urls.items():
        try:
            print(f"Descargando: {filename}")
            
            # Headers para simular un navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Guardar el archivo
            filepath = os.path.join(media_dir, f"{filename}.pdf")
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Descargado: {filename}.pdf ({file_size:,} bytes)")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error descargando {filename}: {e}")
        
        print()
    
    print("=== Resumen ===")
    print(f"Archivos descargados: {success_count}/{len(menu_urls)}")
    
    # Listar archivos descargados
    print("\n=== Archivos en el directorio ===")
    files = [f for f in os.listdir(media_dir) if f.endswith('.pdf')]
    for file in sorted(files):
        filepath = os.path.join(media_dir, file)
        file_size = os.path.getsize(filepath)
        print(f"📄 {file} ({file_size:,} bytes)")

if __name__ == "__main__":
    download_menus()