#!/usr/bin/env python
"""
Script para descargar automáticamente los menús del comedor desde la web de El Gusto de Crecer
"""

import os
import sys
import requests
from urllib.parse import urlparse
from datetime import datetime
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings')
django.setup()

class MenuDownloader:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.media_dir = os.path.join(self.base_dir, 'media', 'comedor')
        
        # Crear directorio si no existe
        os.makedirs(self.media_dir, exist_ok=True)
        
        # URLs de los menús
        self.menu_urls = {
            'septiembre_castellano': 'https://www.elgustodecrecer.es/Users/Menus/Archivos/20250908_134856_BASAL%20SEPTIEMBRE%20in.pdf',
            'septiembre_euskera': 'https://www.elgustodecrecer.es/Users/Menus/Archivos/20250908_135206_BASALA%20IRAILA%20in.pdf'
        }
        
    def download_file(self, url, filename):
        """Descarga un archivo desde una URL"""
        try:
            print(f"Descargando: {url}")
            
            # Headers para simular un navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Lanza excepción si hay error HTTP
            
            # Guardar el archivo
            filepath = os.path.join(self.media_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Descargado: {filename} ({file_size:,} bytes)")
            return True
            
        except requests.RequestException as e:
            print(f"❌ Error descargando {filename}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado con {filename}: {e}")
            return False
    
    def download_all_menus(self):
        """Descarga todos los menús configurados"""
        print("=== Descargador de Menús del Comedor ===")
        print(f"Directorio de destino: {self.media_dir}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        success_count = 0
        total_count = len(self.menu_urls)
        
        for name, url in self.menu_urls.items():
            # Generar nombre de archivo
            filename = f"menu_{name}_{datetime.now().strftime('%Y%m')}.pdf"
            
            if self.download_file(url, filename):
                success_count += 1
            
            print()  # Línea en blanco entre descargas
        
        print("=== Resumen ===")
        print(f"Archivos descargados exitosamente: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("✅ Todas las descargas completadas exitosamente")
        elif success_count > 0:
            print("⚠️ Algunas descargas fallaron")
        else:
            print("❌ No se pudo descargar ningún archivo")
        
        return success_count == total_count
    
    def list_downloaded_files(self):
        """Lista los archivos descargados"""
        print("\n=== Archivos en el directorio de comedor ===")
        
        if not os.path.exists(self.media_dir):
            print("❌ El directorio de comedor no existe")
            return
        
        files = [f for f in os.listdir(self.media_dir) if f.endswith('.pdf')]
        
        if not files:
            print("📁 No hay archivos PDF en el directorio")
            return
        
        for file in sorted(files):
            filepath = os.path.join(self.media_dir, file)
            file_size = os.path.getsize(filepath)
            file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
            print(f"📄 {file}")
            print(f"   Tamaño: {file_size:,} bytes")
            print(f"   Modificado: {file_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print()

def main():
    """Función principal"""
    downloader = MenuDownloader()
    
    # Mostrar archivos existentes
    downloader.list_downloaded_files()
    
    # Descargar menús
    success = downloader.download_all_menus()
    
    # Mostrar archivos después de la descarga
    downloader.list_downloaded_files()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())