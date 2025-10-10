from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys

# Agregar el directorio de scripts al path
scripts_path = os.path.join(settings.BASE_DIR, 'scripts')
sys.path.append(scripts_path)

class Command(BaseCommand):
    help = 'Actualiza los menús del comedor automáticamente'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar descarga incluso si los archivos ya existen',
        )
        parser.add_argument(
            '--simple',
            action='store_true',
            help='Usar el descargador simple (sin login)',
        )
    
    def handle(self, *args, **options):
        try:
            if options['simple']:
                self.stdout.write("🔍 Usando descargador simple (sin login)...")
                from download_menus_simple_new import SimpleMenuDownloader
                downloader = SimpleMenuDownloader()
                success = downloader.download_latest_menus()
            else:
                self.stdout.write("🔍 Usando descargador automático (con login)...")
                from download_menus_automated import AutomatedMenuDownloader
                downloader = AutomatedMenuDownloader()
                
                # Cargar credenciales guardadas
                if downloader.load_credentials():
                    self.stdout.write("✅ Credenciales cargadas desde archivo")
                    success = downloader.download_latest_menus()
                else:
                    self.stdout.write(
                        self.style.ERROR("❌ No se encontraron credenciales guardadas")
                    )
                    self.stdout.write("Ejecuta primero: python manage.py download_menus --setup")
                    return
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS("✅ Menús actualizados exitosamente")
                )
                
                # Mostrar información de los menús descargados
                self.show_menu_status()
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Error actualizando menús")
                )
                
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error importando módulos: {e}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error inesperado: {e}")
            )
    
    def show_menu_status(self):
        """Muestra el estado actual de los menús"""
        media_dir = os.path.join(settings.BASE_DIR, 'media', 'comedor')
        
        if not os.path.exists(media_dir):
            self.stdout.write("❌ Directorio de menús no existe")
            return
        
        files = [f for f in os.listdir(media_dir) if f.endswith('.pdf')]
        
        if not files:
            self.stdout.write("📁 No hay menús en el directorio")
            return
        
        self.stdout.write("\n📋 Menús disponibles:")
        
        from datetime import datetime
        for file in sorted(files):
            filepath = os.path.join(media_dir, file)
            file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
            file_size = os.path.getsize(filepath)
            
            self.stdout.write(
                f"  📄 {file}"
            )
            self.stdout.write(
                f"     Fecha: {file_date.strftime('%Y-%m-%d %H:%M')} | "
                f"Tamaño: {file_size:,} bytes"
            )