#!/usr/bin/env python
"""
Script de configuración y prueba para la descarga automática de menús
"""

import os
import sys
import json
from datetime import datetime

# Agregar el directorio padre al path para importar el script principal
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from download_menus_automated import AutomatedMenuDownloader

def setup_credentials():
    """Configura las credenciales para la descarga automática"""
    print("=== Configuración de Descarga Automática de Menús ===")
    print()
    print("Este script te ayudará a configurar la descarga automática")
    print("de menús desde https://www.elgustodecrecer.es/AreaPersonal")
    print()
    
    email = input("📧 Introduce tu email de acceso: ").strip()
    
    while not email or '@' not in email:
        print("❌ Por favor, introduce un email válido")
        email = input("📧 Email de acceso: ").strip()
    
    import getpass
    password = getpass.getpass("🔑 Introduce tu contraseña: ")
    
    while not password:
        print("❌ La contraseña no puede estar vacía")
        password = getpass.getpass("🔑 Contraseña: ")
    
    print()
    print("🧪 Probando las credenciales...")
    
    # Crear una instancia del descargador para probar
    downloader = AutomatedMenuDownloader(email, password)
    
    if downloader.login():
        print("✅ ¡Credenciales válidas!")
        
        # Guardar credenciales
        if downloader.save_credentials(email, password):
            print("✅ Configuración guardada exitosamente")
            print()
            print("🎉 ¡Ya puedes usar la descarga automática!")
            print("Para descargar menús, ejecuta:")
            print(f"    python {os.path.basename(os.path.dirname(__file__))}/download_menus_automated.py")
            return True
        else:
            print("❌ Error guardando la configuración")
            return False
    else:
        print("❌ Las credenciales no son válidas")
        print("Verifica tu email y contraseña e inténtalo de nuevo")
        return False

def test_download():
    """Prueba la descarga de menús"""
    print("=== Prueba de Descarga de Menús ===")
    print()
    
    downloader = AutomatedMenuDownloader()
    
    if downloader.load_credentials():
        print("✅ Credenciales cargadas desde archivo")
        success = downloader.download_latest_menus()
        if success:
            print("🎉 ¡Descarga de prueba exitosa!")
        else:
            print("❌ La descarga de prueba falló")
        return success
    else:
        print("❌ No se encontraron credenciales guardadas")
        print("Ejecuta primero la configuración:")
        print(f"    python {__file__} --setup")
        return False

def show_status():
    """Muestra el estado actual del sistema"""
    print("=== Estado del Sistema de Descarga ===")
    print()
    
    # Verificar si existen credenciales
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_file = os.path.join(base_dir, '.menu_credentials.json')
    
    if os.path.exists(credentials_file):
        print("✅ Credenciales configuradas")
        try:
            with open(credentials_file, 'r') as f:
                data = json.load(f)
                email = data.get('email', 'No configurado')
                print(f"   Email: {email}")
        except:
            print("⚠️ Error leyendo credenciales")
    else:
        print("❌ Credenciales no configuradas")
    
    # Verificar directorio de menús
    media_dir = os.path.join(base_dir, 'media', 'comedor')
    if os.path.exists(media_dir):
        files = [f for f in os.listdir(media_dir) if f.endswith('.pdf')]
        print(f"📁 Directorio de menús: {media_dir}")
        print(f"   Archivos PDF: {len(files)}")
        
        if files:
            print("   Últimos archivos:")
            for file in sorted(files)[-3:]:  # Mostrar los 3 más recientes
                filepath = os.path.join(media_dir, file)
                file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"     - {file} ({file_date.strftime('%Y-%m-%d %H:%M')})")
    else:
        print("❌ Directorio de menús no existe")
    
    print()
    print("📅 Para automatizar la descarga mensual, puedes:")
    print("   1. Usar el Programador de Tareas de Windows")
    print("   2. Crear un script batch que ejecute el descargador")
    print("   3. Configurar un cron job (en sistemas Unix)")

def create_batch_file():
    """Crea un archivo batch para facilitar la ejecución"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    batch_file = os.path.join(base_dir, 'descargar_menus.bat')
    
    python_path = sys.executable
    script_path = os.path.join(base_dir, 'scripts', 'download_menus_automated.py')
    
    batch_content = f'''@echo off
echo Descargando menus del comedor...
cd /d "{base_dir}"
"{python_path}" "{script_path}"
if %ERRORLEVEL% EQU 0 (
    echo ✅ Descarga completada exitosamente
) else (
    echo ❌ Error en la descarga
)
pause
'''
    
    try:
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        print(f"✅ Archivo batch creado: {batch_file}")
        print("   Puedes hacer doble clic en él para ejecutar la descarga")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo batch: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Configuración de descarga automática de menús')
    parser.add_argument('--setup', action='store_true', help='Configurar credenciales')
    parser.add_argument('--test', action='store_true', help='Probar descarga')
    parser.add_argument('--status', action='store_true', help='Mostrar estado')
    parser.add_argument('--create-batch', action='store_true', help='Crear archivo batch')
    
    args = parser.parse_args()
    
    if args.setup:
        return 0 if setup_credentials() else 1
    elif args.test:
        return 0 if test_download() else 1
    elif args.status:
        show_status()
        return 0
    elif args.create_batch:
        return 0 if create_batch_file() else 1
    else:
        print("Uso del script de configuración:")
        print(f"  python {__file__} --setup        # Configurar credenciales")
        print(f"  python {__file__} --test         # Probar descarga")
        print(f"  python {__file__} --status       # Ver estado")
        print(f"  python {__file__} --create-batch # Crear archivo batch")
        return 1

if __name__ == "__main__":
    exit(main())