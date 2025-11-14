import os
import subprocess
import sys

# Añadir directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings')

try:
    import django
    django.setup()
    from django.core.management import call_command
    
    # Compilar solo euskera
    call_command('compilemessages', locale=['eu'], verbosity=2)
    print("\n✓ Traducciones de euskera compiladas correctamente")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
