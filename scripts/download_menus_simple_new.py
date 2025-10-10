#!/usr/bin/env python
"""
Script simple para descargar menús sin login (URLs públicas)
Este script se puede usar cuando los menús están disponibles públicamente
"""

import os
import sys
import requests
import re
from datetime import datetime
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings')
django.setup()

class SimpleMenuDownloader:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.media_dir = os.path.join(self.base_dir, 'media', 'comedor')
        
        # Crear directorio si no existe
        os.makedirs(self.media_dir, exist_ok=True)
        
        self.base_url = "https://www.elgustodecrecer.es"
        
        # Sesión para requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
    
    def find_current_month_menus(self):
        """Busca menús del mes actual usando patrones inteligentes"""
        menu_links = []
        current_date = datetime.now()
        
        # Información del mes actual
        month_names = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO',
            7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
        }
        
        year = current_date.year
        month = current_date.month
        month_name = month_names.get(month, '')
        
        print(f"🗓️ Buscando menús para {month_name} {year}...")
        
        # Patrones de nombre de archivo
        file_patterns = [
            'BASAL%20REMONTIVAL%20{month}',
            'BASAL%20{month}',
            'MENU%20REMONTIVAL%20{month}',
            'MENU%20{month}',
            'REMONTIVAL%20{month}',
            '{month}%20REMONTIVAL',
            '{month}%20BASAL'
        ]
        
        base_archive_url = f"{self.base_url}/Users/Menus/Archivos/"
        
        for pattern in file_patterns:
            filename_part = pattern.format(month=month_name)
            
            # Buscar desde el día actual hacia atrás
            days_to_check = list(range(current_date.day, 0, -1))
            
            for day in days_to_check[:15]:  # Limitar a los últimos 15 días
                date_prefix = f"{year:04d}{month:02d}{day:02d}"
                
                # Patrones de hora más comunes
                time_patterns = ['152623', '150000', '120000', '134856', '135206', '100000', '140000', '160000', '090000', '110000']
                
                for time_part in time_patterns:
                    url_candidate = f"{base_archive_url}{date_prefix}_{time_part}_{filename_part}.pdf"
                    
                    try:
                        # Verificar si la URL existe
                        response = self.session.head(url_candidate, timeout=5)
                        if response.status_code == 200:
                            menu_links.append({
                                'url': url_candidate,
                                'text': f"Menu {month_name.title()} {year}",
                                'pattern': pattern,
                                'date': f"{year}-{month:02d}-{day:02d}",
                                'time': time_part
                            })
                            print(f"✅ Encontrado: Menu {month_name.title()} {year} (fecha: {day:02d}/{month:02d}/{year})")
                            # Una vez encontrado, pasar al siguiente patrón
                            break
                    except:
                        continue  # URL no existe, continuar
                else:
                    continue  # No break, seguir con el siguiente día
                break  # Se encontró, salir del loop de días
        
        # Si no se encontró nada del mes actual, buscar el mes anterior
        if not menu_links:
            print(f"⚠️ No se encontraron menús para {month_name}, buscando mes anterior...")
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            prev_month_name = month_names.get(prev_month, '')
            
            menu_links.extend(self._search_month_menus(prev_year, prev_month, prev_month_name))
        
        return menu_links
    
    def _search_month_menus(self, year, month, month_name):
        """Busca menús de un mes específico"""
        menu_links = []
        
        file_patterns = [
            'BASAL%20REMONTIVAL%20{month}',
            'BASAL%20{month}',
            'MENU%20REMONTIVAL%20{month}',
        ]
        
        base_archive_url = f"{self.base_url}/Users/Menus/Archivos/"
        
        for pattern in file_patterns:
            filename_part = pattern.format(month=month_name)
            
            # Días más probables de publicación
            days_to_check = [1, 2, 3, 15, 30, 31]
            
            for day in days_to_check:
                if day > 31:
                    continue
                    
                date_prefix = f"{year:04d}{month:02d}{day:02d}"
                time_patterns = ['152623', '150000', '120000', '134856']
                
                for time_part in time_patterns:
                    url_candidate = f"{base_archive_url}{date_prefix}_{time_part}_{filename_part}.pdf"
                    
                    try:
                        response = self.session.head(url_candidate, timeout=5)
                        if response.status_code == 200:
                            menu_links.append({
                                'url': url_candidate,
                                'text': f"Menu {month_name.title()} {year}",
                                'pattern': pattern,
                                'date': f"{year}-{month:02d}-{day:02d}",
                                'time': time_part
                            })
                            print(f"✅ Encontrado: Menu {month_name.title()} {year}")
                            break
                    except:
                        continue
                else:
                    continue
                break
        
        return menu_links
    
    def download_menu(self, menu_data):
        """Descarga un menú específico"""
        try:
            url = menu_data['url']
            text = menu_data['text']
            
            print(f"📥 Descargando: {text}")
            
            # Generar nombre de archivo
            clean_text = re.sub(r'[^\w\s-]', '', text).strip()
            clean_text = re.sub(r'[-\s]+', '_', clean_text)
            
            # Incluir la fecha en el nombre del archivo
            date_part = menu_data['date'].replace('-', '')
            filename = f"menu_{clean_text}_{date_part}.pdf"
            filepath = os.path.join(self.media_dir, filename)
            
            # Verificar si ya existe
            if os.path.exists(filepath):
                existing_size = os.path.getsize(filepath)
                print(f"⏭️ Archivo ya existe: {filename} ({existing_size:,} bytes)")
                return True
            
            # Descargar
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Guardar
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Descargado: {filename} ({file_size:,} bytes)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error descargando {menu_data['text']}: {e}")
            return False
    
    def download_latest_menus(self):
        """Descarga los menús más recientes disponibles"""
        print("=== Descargador Simple de Menús ===")
        print(f"Directorio de destino: {self.media_dir}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Buscar menús
        menu_links = self.find_current_month_menus()
        
        if not menu_links:
            print("❌ No se encontraron menús disponibles")
            return False
        
        print(f"\n📋 Encontrados {len(menu_links)} menús:")
        for i, menu in enumerate(menu_links, 1):
            print(f"  {i}. {menu['text']} (fecha: {menu['date']})")
        print()
        
        # Descargar menús
        success_count = 0
        for menu_data in menu_links:
            if self.download_menu(menu_data):
                success_count += 1
        
        print()
        print("=== Resumen ===")
        print(f"Menús descargados: {success_count}/{len(menu_links)}")
        
        if success_count > 0:
            print("✅ Descarga completada")
            return True
        else:
            print("❌ No se descargó ningún menú")
            return False

def main():
    """Función principal"""
    downloader = SimpleMenuDownloader()
    success = downloader.download_latest_menus()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())