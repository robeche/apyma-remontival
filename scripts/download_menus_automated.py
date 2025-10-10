#!/usr/bin/env python
"""
Script para automatizar la descarga de menús desde el área personal de El Gusto de Crecer
Requiere credenciales de login para acceder al área personal
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import django
from urllib.parse import urljoin, urlparse
import time
import json
from pypdf import PdfReader, PdfWriter

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings')
django.setup()

class AutomatedMenuDownloader:
    def __init__(self, email=None, password=None):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.media_dir = os.path.join(self.base_dir, 'media', 'comedor')
        
        # Crear directorio si no existe
        os.makedirs(self.media_dir, exist_ok=True)
        
        # Configuración de login
        self.email = email
        self.password = password
        self.base_url = "https://www.elgustodecrecer.es"
        self.login_url = f"{self.base_url}/AreaPersonal"
        
        # Sesión para mantener cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
        
        # Archivo para guardar credenciales de forma segura
        self.credentials_file = os.path.join(self.base_dir, '.menu_credentials.json')
        
    def load_credentials(self):
        """Carga las credenciales desde archivo si existen"""
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                    self.email = data.get('email')
                    self.password = data.get('password')
                    return True
            except Exception as e:
                print(f"⚠️ Error cargando credenciales: {e}")
        return False
    
    def save_credentials(self, email, password):
        """Guarda las credenciales de forma segura"""
        try:
            data = {
                'email': email,
                'password': password
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f)
            
            # Cambiar permisos para que solo el usuario pueda leer
            if os.name != 'nt':  # Unix/Linux
                os.chmod(self.credentials_file, 0o600)
                
            print("✅ Credenciales guardadas de forma segura")
            return True
        except Exception as e:
            print(f"❌ Error guardando credenciales: {e}")
            return False
    
    def login(self):
        """Realiza el login en el área personal"""
        try:
            print("🔐 Iniciando sesión en El Gusto de Crecer...")
            
            # Primero, obtener la página de login para extraer tokens CSRF si es necesario
            response = self.session.get(self.login_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar el formulario de login
            login_form = soup.find('form')
            if not login_form:
                print("❌ No se encontró formulario de login")
                return False
            
            # Extraer la action del formulario
            form_action = login_form.get('action', '')
            if form_action:
                login_post_url = urljoin(self.base_url, form_action)
            else:
                login_post_url = self.login_url
            
            # Buscar campos ocultos (tokens CSRF, etc.)
            hidden_fields = {}
            for input_field in login_form.find_all('input', type='hidden'):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    hidden_fields[name] = value
            
            # Buscar los nombres de los campos de email y password
            email_field = login_form.find('input', {'type': 'email'}) or login_form.find('input', {'name': re.compile(r'email|usuario|user', re.I)})
            password_field = login_form.find('input', {'type': 'password'}) or login_form.find('input', {'name': re.compile(r'password|pass|contraseña', re.I)})
            
            if not email_field or not password_field:
                print("❌ No se encontraron campos de email/password")
                return False
            
            email_field_name = email_field.get('name', 'email')
            password_field_name = password_field.get('name', 'password')
            
            # Datos del formulario
            form_data = {
                email_field_name: self.email,
                password_field_name: self.password,
                **hidden_fields
            }
            
            print(f"📧 Enviando credenciales a: {login_post_url}")
            
            # Realizar el login
            response = self.session.post(
                login_post_url,
                data=form_data,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Verificar si el login fue exitoso
            # Buscar indicadores de login exitoso
            success_indicators = [
                'logout', 'cerrar sesión', 'salir', 'mi cuenta', 'perfil',
                'área personal', 'dashboard', 'menús'
            ]
            
            page_text = response.text.lower()
            login_success = any(indicator in page_text for indicator in success_indicators)
            
            # También verificar si seguimos en la página de login
            login_failed_indicators = [
                'error de login', 'credenciales incorrectas', 'usuario o contraseña',
                'email o password', 'acceso denegado'
            ]
            login_failed = any(indicator in page_text for indicator in login_failed_indicators)
            
            if login_failed:
                print("❌ Login fallido: credenciales incorrectas")
                return False
            
            if login_success or response.url != self.login_url:
                print("✅ Login exitoso")
                return True
            else:
                print("⚠️ Estado de login incierto, continuando...")
                return True
                
        except Exception as e:
            print(f"❌ Error durante el login: {e}")
            return False
    
    def find_menu_links(self):
        """Busca enlaces a menús en el área personal y URLs directas"""
        try:
            print("🔍 Buscando menús disponibles...")
            
            menu_links = []
            
            # Estrategia 1: Buscar en URLs directas conocidas (más confiable)
            print("📁 Buscando en URLs directas conocidas...")
            direct_menu_patterns = self.find_direct_menu_urls()
            menu_links.extend(direct_menu_patterns)
            
            # Estrategia 2: Buscar en el área personal
            print("🔐 Buscando en área personal...")
            personal_area_links = self.find_personal_area_menus()
            menu_links.extend(personal_area_links)
            
            # Eliminar duplicados
            unique_links = []
            seen_urls = set()
            for link in menu_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            return unique_links
            
        except Exception as e:
            print(f"❌ Error buscando menús: {e}")
            return []
    
    def find_direct_menu_urls(self):
        """Busca menús usando patrones de URL directas conocidas"""
        menu_links = []
        
        # Estrategia 1: Explorar el directorio de archivos para encontrar menús automáticamente
        print("🔍 Explorando directorio de menús...")
        discovered_menus = self.discover_menus_from_directory()
        menu_links.extend(discovered_menus)
        
        # Estrategia 2: Patrones de URL basados en el formato conocido
        print("📅 Buscando con patrones de fecha...")
        pattern_menus = self.find_menus_by_date_patterns()
        menu_links.extend(pattern_menus)
        
        return menu_links
    
    def discover_menus_from_directory(self):
        """Intenta descubrir menús explorando el directorio web"""
        menu_links = []
        base_archive_url = f"{self.base_url}/Users/Menus/Archivos/"
        
        try:
            # Intentar acceder al directorio de archivos
            response = self.session.get(base_archive_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar enlaces a archivos PDF
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    # Filtrar solo PDFs de menús
                    if (href and href.endswith('.pdf') and 
                        any(keyword in href.upper() for keyword in ['BASAL', 'MENU', 'REMONTIVAL'])):
                        
                        # Extraer información del nombre del archivo
                        full_url = urljoin(base_archive_url, href)
                        
                        # Intentar extraer el mes del nombre del archivo
                        month_match = re.search(r'(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)', href.upper())
                        
                        if month_match:
                            month_name = month_match.group(1).title()
                            display_text = f"Menu {month_name} 2025"
                        else:
                            display_text = text or "Menu del Comedor"
                        
                        menu_links.append({
                            'url': full_url,
                            'text': display_text,
                            'source_page': 'directory_listing'
                        })
                        print(f"✅ Descubierto en directorio: {display_text}")
                        
        except Exception as e:
            print(f"⚠️ No se pudo explorar el directorio: {e}")
        
        return menu_links
    
    def find_menus_by_date_patterns(self):
        """Busca menús usando patrones de fecha inteligentes"""
        menu_links = []
        
        # Patrones de URL basados en el formato conocido
        current_date = datetime.now()
        
        # Generar posibles URLs para el mes actual y siguiente
        months_to_check = [
            (current_date.year, current_date.month),
        ]
        
        # Si estamos en los últimos días del mes, también buscar el siguiente
        if current_date.day > 25:
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year if current_date.month < 12 else current_date.year + 1
            months_to_check.append((next_year, next_month))
        
        month_names = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO',
            7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
        }
        
        # Patrones de nombre de archivo más completos
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
        
        for year, month in months_to_check:
            month_name = month_names.get(month, '')
            print(f"🗓️ Buscando menús para {month_name} {year}...")
            
            for pattern in file_patterns:
                filename_part = pattern.format(month=month_name)
                
                # Generar posibles URLs con diferentes fechas del mes
                # Buscar en fechas más probables primero
                days_to_check = []
                
                # Si es el mes actual, buscar desde el día actual hacia atrás
                if year == current_date.year and month == current_date.month:
                    days_to_check = list(range(current_date.day, 0, -1))  # Del día actual hacia atrás
                else:
                    days_to_check = [1, 2, 3, 15, 30, 31]  # Días típicos de publicación
                
                for day in days_to_check[:10]:  # Limitar a 10 intentos por patrón
                    if day > 31:
                        continue
                        
                    date_prefix = f"{year:04d}{month:02d}{day:02d}"
                    
                    # Diferentes formatos de hora (ordenados por probabilidad)
                    time_patterns = ['152623', '150000', '120000', '134856', '135206', '100000', '140000', '160000']
                    
                    for time_part in time_patterns:
                        url_candidate = f"{base_archive_url}{date_prefix}_{time_part}_{filename_part}.pdf"
                        
                        try:
                            # Verificar si la URL existe (HEAD request es más rápido)
                            response = self.session.head(url_candidate, timeout=5)
                            if response.status_code == 200:
                                menu_links.append({
                                    'url': url_candidate,
                                    'text': f"Menu {month_name.title()} {year}",
                                    'source_page': 'pattern_search'
                                })
                                print(f"✅ Encontrado por patrón: Menu {month_name.title()} {year}")
                                # Una vez encontrado el menú del mes, pasar al siguiente mes
                                break
                        except:
                            continue  # URL no existe, continuar
                    else:
                        continue  # No break, seguir con el siguiente tiempo
                    break  # Se encontró, salir del loop de días
                else:
                    continue  # No break, seguir con el siguiente patrón
                break  # Se encontró, salir del loop de patrones
        
        return menu_links
    
    def find_personal_area_menus(self):
        """Busca menús en el área personal después del login"""
        menu_links = []
        
        # Intentar diferentes URLs del área personal
        possible_urls = [
            f"{self.base_url}/AreaPersonal",
            f"{self.base_url}/menus",
            f"{self.base_url}/documentos",
            f"{self.base_url}/descargas",
            f"{self.base_url}/Users/Menus"
        ]
        
        for url in possible_urls:
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Buscar enlaces a PDFs de múltiples formas
                    pdf_links = []
                    
                    # Método 1: Enlaces directos a PDF
                    pdf_links.extend(soup.find_all('a', href=re.compile(r'\.pdf$', re.I)))
                    
                    # Método 2: Enlaces que contienen "pdf" en el href
                    pdf_links.extend(soup.find_all('a', href=re.compile(r'pdf', re.I)))
                    
                    # Método 3: Buscar enlaces en el directorio de menús
                    menu_dir_links = soup.find_all('a', href=re.compile(r'/Users/Menus/', re.I))
                    pdf_links.extend(menu_dir_links)
                    
                    for link in pdf_links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        
                        if not href:
                            continue
                            
                        # Filtrar solo menús (buscar palabras clave)
                        menu_keywords = ['menu', 'menú', 'comedor', 'basal', 'alimentación', 'remontival']
                        text_lower = text.lower()
                        href_lower = href.lower()
                        
                        if (any(keyword in text_lower for keyword in menu_keywords) or
                            any(keyword in href_lower for keyword in menu_keywords)):
                            
                            full_url = urljoin(self.base_url, href)
                            menu_links.append({
                                'url': full_url,
                                'text': text or 'Menu del comedor',
                                'source_page': url
                            })
                            
            except Exception as e:
                print(f"⚠️ Error verificando {url}: {e}")
                continue
        
        return menu_links
    
    def split_menu_pdf(self, pdf_path, menu_text):
        """Separa un PDF de menú en castellano y euskera"""
        try:
            print(f"📄 Separando páginas del PDF: {os.path.basename(pdf_path)}")
            
            # Leer el PDF
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            
            print(f"   Total de páginas: {total_pages}")
            
            if total_pages < 2:
                print(f"⚠️ El PDF solo tiene {total_pages} página(s), no se puede separar")
                return False
            
            # Extraer el mes del texto del menú
            month_match = re.search(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)', menu_text.lower())
            if month_match:
                month_name = month_match.group(1)
            else:
                # Fallback: usar mes actual
                month_names = {
                    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
                    7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
                }
                month_name = month_names.get(datetime.now().month, 'mes')
            
            # Crear directorio base para los archivos separados
            base_dir = os.path.dirname(pdf_path)
            
            # Crear PDF para castellano (primera página)
            castellano_filename = f"menu_{month_name}_castellano.pdf"
            castellano_path = os.path.join(base_dir, castellano_filename)
            
            writer_castellano = PdfWriter()
            writer_castellano.add_page(reader.pages[0])
            
            with open(castellano_path, 'wb') as output_file:
                writer_castellano.write(output_file)
            
            print(f"✅ Creado: {castellano_filename}")
            
            # Crear PDF para euskera (segunda página)
            euskera_filename = f"menu_{month_name}_euskera.pdf"
            euskera_path = os.path.join(base_dir, euskera_filename)
            
            writer_euskera = PdfWriter()
            writer_euskera.add_page(reader.pages[1])
            
            with open(euskera_path, 'wb') as output_file:
                writer_euskera.write(output_file)
            
            print(f"✅ Creado: {euskera_filename}")
            
            # Si hay más páginas, crear un PDF con todas las páginas adicionales
            if total_pages > 2:
                extra_filename = f"menu_{month_name}_adicional.pdf"
                extra_path = os.path.join(base_dir, extra_filename)
                
                writer_extra = PdfWriter()
                for page_num in range(2, total_pages):
                    writer_extra.add_page(reader.pages[page_num])
                
                with open(extra_path, 'wb') as output_file:
                    writer_extra.write(output_file)
                
                print(f"✅ Creado: {extra_filename} (páginas adicionales)")
            
            # Opcional: eliminar el archivo original después de separar
            try:
                os.remove(pdf_path)
                print(f"🗑️ Eliminado archivo original: {os.path.basename(pdf_path)}")
            except:
                print(f"⚠️ No se pudo eliminar el archivo original: {os.path.basename(pdf_path)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error separando PDF: {e}")
            return False
            
    def download_menu(self, menu_link):
        """Descarga un menú específico y separa las páginas en castellano y euskera"""
        try:
            url = menu_link['url']
            text = menu_link['text']
            
            print(f"📥 Descargando: {text}")
            print(f"    URL: {url}")
            
            # Generar nombre de archivo temporal
            current_month = datetime.now().strftime('%Y%m')
            
            # Limpiar el texto para el nombre del archivo
            clean_text = re.sub(r'[^\w\s-]', '', text).strip()
            clean_text = re.sub(r'[-\s]+', '_', clean_text)
            
            temp_filename = f"menu_{clean_text}_{current_month}_temp.pdf"
            temp_filepath = os.path.join(self.media_dir, temp_filename)
            
            # Extraer nombre del mes para los archivos separados
            month_match = re.search(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)', text.lower())
            if month_match:
                month_name = month_match.group(1)
            else:
                # Fallback: usar mes actual
                month_names = {
                    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
                    7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
                }
                month_name = month_names.get(datetime.now().month, 'mes')
            
            # Verificar si los archivos separados ya existen
            castellano_filepath = os.path.join(self.media_dir, f"menu_{month_name}_castellano.pdf")
            euskera_filepath = os.path.join(self.media_dir, f"menu_{month_name}_euskera.pdf")
            
            if os.path.exists(castellano_filepath) and os.path.exists(euskera_filepath):
                print(f"⏭️ Los archivos separados ya existen:")
                print(f"   - {os.path.basename(castellano_filepath)}")
                print(f"   - {os.path.basename(euskera_filepath)}")
                
                # Verificar tamaños para asegurarse de que están completos
                castellano_size = os.path.getsize(castellano_filepath)
                euskera_size = os.path.getsize(euskera_filepath)
                
                if castellano_size > 10000 and euskera_size > 10000:  # Al menos 10KB cada uno
                    print(f"   Archivos válidos (tamaños: {castellano_size:,} y {euskera_size:,} bytes)")
                    return True
                else:
                    print(f"   ⚠️ Archivos parecen incompletos, re-descargando...")
            
            # Descargar el archivo
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Guardar el archivo temporal
            with open(temp_filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Descargado archivo temporal: {temp_filename} ({file_size:,} bytes)")
            
            # Separar las páginas
            if self.split_menu_pdf(temp_filepath, text):
                print(f"✅ Menú separado exitosamente en castellano y euskera")
                return True
            else:
                print(f"❌ Error separando el menú")
                return False
            
        except Exception as e:
            print(f"❌ Error descargando {menu_link['text']}: {e}")
            return False
    
    def download_latest_menus(self):
        """Descarga los menús más recientes"""
        print("=== Descargador Automático de Menús ===")
        print(f"Directorio de destino: {self.media_dir}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Verificar credenciales
        if not self.email or not self.password:
            if not self.load_credentials():
                self.email = input("📧 Email de acceso: ").strip()
                self.password = input("🔑 Contraseña: ").strip()
                
                save_creds = input("💾 ¿Guardar credenciales para futuras ejecuciones? (s/n): ").strip().lower()
                if save_creds in ['s', 'si', 'sí', 'y', 'yes']:
                    self.save_credentials(self.email, self.password)
        
        # Realizar login
        if not self.login():
            print("❌ No se pudo realizar el login")
            return False
        
        # Buscar menús
        menu_links = self.find_menu_links()
        
        if not menu_links:
            print("❌ No se encontraron menús disponibles")
            return False
        
        print(f"📋 Encontrados {len(menu_links)} menús:")
        for i, menu in enumerate(menu_links, 1):
            print(f"  {i}. {menu['text']}")
        print()
        
        # Descargar menús
        success_count = 0
        for menu_link in menu_links:
            if self.download_menu(menu_link):
                success_count += 1
            time.sleep(1)  # Pausa entre descargas
        
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Descargador automático de menús')
    parser.add_argument('--email', help='Email de acceso')
    parser.add_argument('--password', help='Contraseña de acceso')
    
    args = parser.parse_args()
    
    downloader = AutomatedMenuDownloader(args.email, args.password)
    success = downloader.download_latest_menus()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())