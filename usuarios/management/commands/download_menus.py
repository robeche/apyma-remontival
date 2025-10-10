from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys

# Agregar el directorio de scripts al path
scripts_path = os.path.join(settings.BASE_DIR, 'scripts')
sys.path.append(scripts_path)

from download_menus_automated import AutomatedMenuDownloader

class Command(BaseCommand):
    help = 'Descarga automáticamente los menús del comedor desde El Gusto de Crecer'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de acceso al área personal',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Contraseña de acceso',
        )
        parser.add_argument(
            '--setup',
            action='store_true',
            help='Configurar credenciales interactivamente',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Mostrar estado de los menús descargados',
        )
    
    def handle(self, *args, **options):
        if options['setup']:
            self.setup_credentials()
        elif options['status']:
            self.show_status()
        else:
            self.download_menus(options['email'], options['password'])
    
    def setup_credentials(self):
        """Configurar credenciales interactivamente"""
        self.stdout.write(
            self.style.SUCCESS('=== Configuración de Descarga de Menús ===')
        )
        
        email = input("📧 Email de acceso: ").strip()
        if not email or '@' not in email:
            self.stdout.write(
                self.style.ERROR('❌ Email inválido')
            )
            return
        
        import getpass
        password = getpass.getpass("🔑 Contraseña: ")
        if not password:
            self.stdout.write(
                self.style.ERROR('❌ Contraseña requerida')
            )
            return
        
        downloader = AutomatedMenuDownloader(email, password)
        if downloader.save_credentials(email, password):
            self.stdout.write(
                self.style.SUCCESS('✅ Credenciales guardadas exitosamente')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Error guardando credenciales')
            )
    
    def download_menus(self, email=None, password=None):
        """Descargar menús"""
        self.stdout.write(
            self.style.SUCCESS('=== Descarga de Menús del Comedor ===')
        )
        
        downloader = AutomatedMenuDownloader(email, password)
        
        try:
            success = downloader.download_latest_menus()
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Menús descargados exitosamente')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Error en la descarga de menús')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )
    
    def show_status(self):
        """Mostrar estado de los menús"""
        self.stdout.write(
            self.style.SUCCESS('=== Estado de los Menús ===')
        )
        
        media_dir = os.path.join(settings.BASE_DIR, 'media', 'comedor')
        
        if not os.path.exists(media_dir):
            self.stdout.write(
                self.style.WARNING('❌ Directorio de menús no existe')
            )
            return
        
        files = [f for f in os.listdir(media_dir) if f.endswith('.pdf')]
        
        if not files:
            self.stdout.write(
                self.style.WARNING('📁 No hay menús descargados')
            )
            return
        
        self.stdout.write(f'📁 Menús encontrados: {len(files)}')
        
        from datetime import datetime
        for file in sorted(files):
            filepath = os.path.join(media_dir, file)
            file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
            file_size = os.path.getsize(filepath)
            
            self.stdout.write(
                f'  📄 {file}'
            )
            self.stdout.write(
                f'     Fecha: {file_date.strftime("%Y-%m-%d %H:%M")} | '
                f'Tamaño: {file_size:,} bytes'
            )