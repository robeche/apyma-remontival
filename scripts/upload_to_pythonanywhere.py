#!/usr/bin/env python
"""
Script para subir menús a PythonAnywhere automáticamente
Este script se ejecuta en tu PC local y sube los archivos via SCP/SFTP
"""

import os
import sys
import paramiko
import json
from datetime import datetime
import getpass

class PythonAnywhereUploader:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.local_media_dir = os.path.join(self.base_dir, 'media', 'comedor')
        
        # Configuración de PythonAnywhere
        self.pa_config_file = os.path.join(self.base_dir, '.pythonanywhere_config.json')
        
        # Configuración por defecto (puedes cambiarla)
        self.default_config = {
            'hostname': 'ssh.pythonanywhere.com',
            'username': 'tu_usuario_pa',  # Cambiar por tu usuario
            'remote_path': '/home/tu_usuario_pa/apyma-remontival/media/comedor/',
            'port': 22
        }
    
    def load_config(self):
        """Carga la configuración de PythonAnywhere"""
        if os.path.exists(self.pa_config_file):
            try:
                with open(self.pa_config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error cargando configuración: {e}")
        return self.default_config
    
    def save_config(self, config):
        """Guarda la configuración de PythonAnywhere"""
        try:
            with open(self.pa_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Configuración guardada")
            return True
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            return False
    
    def setup_config(self):
        """Configura la conexión a PythonAnywhere"""
        print("=== Configuración de PythonAnywhere ===")
        print()
        
        username = input("Usuario de PythonAnywhere: ").strip()
        if not username:
            print("❌ Usuario requerido")
            return False
        
        password = getpass.getpass("Contraseña de PythonAnywhere: ")
        if not password:
            print("❌ Contraseña requerida")
            return False
        
        # Ruta remota por defecto
        remote_path = f"/home/{username}/apyma-remontival/media/comedor/"
        custom_path = input(f"Ruta remota [{remote_path}]: ").strip()
        if custom_path:
            remote_path = custom_path
        
        config = {
            'hostname': 'ssh.pythonanywhere.com',
            'username': username,
            'password': password,  # En producción, mejor usar claves SSH
            'remote_path': remote_path,
            'port': 22
        }
        
        # Probar conexión
        print("\n🧪 Probando conexión...")
        if self.test_connection(config):
            print("✅ Conexión exitosa")
            self.save_config(config)
            return True
        else:
            print("❌ Error en la conexión")
            return False
    
    def test_connection(self, config):
        """Prueba la conexión SSH a PythonAnywhere"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=config['hostname'],
                username=config['username'],
                password=config.get('password'),
                port=config['port'],
                timeout=30
            )
            
            # Probar comando simple
            stdin, stdout, stderr = ssh.exec_command('ls -la')
            stdout.read()
            
            ssh.close()
            return True
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def upload_menus(self, force=False):
        """Sube los menús más recientes a PythonAnywhere"""
        print("=== Subida de Menús a PythonAnywhere ===")
        print(f"Directorio local: {self.local_media_dir}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Cargar configuración
        config = self.load_config()
        
        if not config.get('username') or config['username'] == 'tu_usuario_pa':
            print("❌ Configuración no encontrada. Ejecuta --setup primero")
            return False
        
        # Buscar archivos de menú locales
        if not os.path.exists(self.local_media_dir):
            print("❌ Directorio local de menús no existe")
            return False
        
        pdf_files = [f for f in os.listdir(self.local_media_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("❌ No hay archivos PDF para subir")
            return False
        
        # Encontrar los menús más recientes
        recent_menus = self.find_recent_menus(pdf_files)
        
        if not recent_menus:
            print("❌ No se encontraron menús recientes")
            return False
        
        print(f"📋 Menús a subir: {len(recent_menus)}")
        for menu in recent_menus:
            print(f"  📄 {menu}")
        print()
        
        # Conectar y subir archivos
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            print("🔗 Conectando a PythonAnywhere...")
            ssh.connect(
                hostname=config['hostname'],
                username=config['username'],
                password=config.get('password'),
                port=config['port'],
                timeout=30
            )
            
            # Crear cliente SFTP
            sftp = ssh.open_sftp()
            
            # Crear directorio remoto si no existe
            try:
                sftp.makedirs(config['remote_path'])
            except:
                pass  # Directorio ya existe
            
            # Subir archivos
            success_count = 0
            for menu_file in recent_menus:
                local_path = os.path.join(self.local_media_dir, menu_file)
                remote_file_path = config['remote_path'] + menu_file
                
                try:
                    print(f"📤 Subiendo: {menu_file}")
                    
                    # Verificar si el archivo remoto existe y es igual
                    if not force:
                        try:
                            remote_stat = sftp.stat(remote_file_path)
                            local_stat = os.stat(local_path)
                            
                            if remote_stat.st_size == local_stat.st_size:
                                print(f"⏭️ Archivo ya existe con el mismo tamaño: {menu_file}")
                                success_count += 1
                                continue
                        except:
                            pass  # Archivo remoto no existe
                    
                    # Subir archivo
                    sftp.put(local_path, remote_file_path)
                    
                    # Verificar que se subió correctamente
                    remote_stat = sftp.stat(remote_file_path)
                    local_size = os.path.getsize(local_path)
                    
                    if remote_stat.st_size == local_size:
                        print(f"✅ Subido correctamente: {menu_file} ({local_size:,} bytes)")
                        success_count += 1
                    else:
                        print(f"❌ Error en la subida: {menu_file} (tamaños no coinciden)")
                    
                except Exception as e:
                    print(f"❌ Error subiendo {menu_file}: {e}")
            
            sftp.close()
            ssh.close()
            
            print()
            print("=== Resumen ===")
            print(f"Archivos subidos exitosamente: {success_count}/{len(recent_menus)}")
            
            if success_count > 0:
                print("✅ Subida completada")
                print("🌐 Los menús deberían estar disponibles en tu web en unos minutos")
                return True
            else:
                print("❌ No se subió ningún archivo")
                return False
            
        except Exception as e:
            print(f"❌ Error durante la subida: {e}")
            return False
    
    def find_recent_menus(self, pdf_files):
        """Encuentra los menús más recientes"""
        import re
        
        # Agrupar por mes
        menus_por_mes = {}
        
        for pdf_file in pdf_files:
            # Extraer mes del nombre del archivo
            match = re.match(r'menu_(\w+)_(castellano|euskera)\.pdf', pdf_file, re.IGNORECASE)
            
            if match:
                mes, idioma = match.groups()
                
                if mes not in menus_por_mes:
                    menus_por_mes[mes] = []
                
                # Obtener fecha de modificación
                file_path = os.path.join(self.local_media_dir, pdf_file)
                file_mtime = os.path.getmtime(file_path)
                
                menus_por_mes[mes].append({
                    'archivo': pdf_file,
                    'fecha_mod': file_mtime,
                    'idioma': idioma
                })
        
        # Encontrar el mes más reciente
        if not menus_por_mes:
            return []
        
        mes_mas_reciente = None
        fecha_mas_reciente = 0
        
        for mes, archivos in menus_por_mes.items():
            max_fecha = max(info['fecha_mod'] for info in archivos)
            if max_fecha > fecha_mas_reciente:
                fecha_mas_reciente = max_fecha
                mes_mas_reciente = mes
        
        # Retornar archivos del mes más reciente
        if mes_mas_reciente:
            return [info['archivo'] for info in menus_por_mes[mes_mas_reciente]]
        
        return []

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Subir menús a PythonAnywhere')
    parser.add_argument('--setup', action='store_true', help='Configurar conexión a PythonAnywhere')
    parser.add_argument('--force', action='store_true', help='Forzar subida (sobrescribir archivos)')
    parser.add_argument('--test', action='store_true', help='Probar conexión')
    
    args = parser.parse_args()
    
    uploader = PythonAnywhereUploader()
    
    if args.setup:
        return 0 if uploader.setup_config() else 1
    elif args.test:
        config = uploader.load_config()
        return 0 if uploader.test_connection(config) else 1
    else:
        return 0 if uploader.upload_menus(args.force) else 1

if __name__ == "__main__":
    exit(main())