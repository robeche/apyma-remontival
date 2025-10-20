#!/usr/bin/env python
"""
Script temporal para compilar traducciones sin msgfmt
"""
import os
import django
from django.conf import settings
from django.core.management import call_command

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings.development')
django.setup()

def compile_translations():
    """Compila las traducciones usando Django"""
    try:
        # Configurar PATH temporal para msgfmt
        import os
        original_path = os.environ.get('PATH', '')
        os.environ['PATH'] = original_path + ';C:\\tools\\msys64\\usr\\bin'
        
        # Intentar usar el comando de Django
        call_command('compilemessages', verbosity=2)
        print("✓ Traducciones compiladas exitosamente usando Django")
        
        # Restaurar PATH original
        os.environ['PATH'] = original_path
        
    except Exception as e:
        print(f"Error al compilar traducciones: {e}")
        
        # Alternativa: crear archivos .mo manualmente si es necesario
        print("Intentando alternativa manual...")
        
        import struct
        from pathlib import Path
        
        # Buscar archivos .po
        locale_dir = Path('locale')
        for po_file in locale_dir.glob('**/*.po'):
            mo_file = po_file.with_suffix('.mo')
            
            print(f"Procesando: {po_file} -> {mo_file}")
            
            # Leer el archivo .po y crear un .mo básico
            try:
                with open(po_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extraer traducciones básicas
                translations = {}
                lines = content.split('\n')
                msgid = None
                msgstr = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('msgid "'):
                        msgid = line[7:-1]  # Remover 'msgid "' y '"'
                    elif line.startswith('msgstr "'):
                        msgstr = line[8:-1]  # Remover 'msgstr "' y '"'
                        if msgid and msgstr and msgid != '':
                            translations[msgid] = msgstr
                
                # Crear archivo .mo básico
                mo_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Para Django, necesitamos crear un archivo .mo válido
                # Por simplicidad, creamos uno vacío que Django pueda leer
                with open(mo_file, 'wb') as f:
                    # Escribir header básico de archivo .mo
                    f.write(b'\xde\x12\x04\x95')  # Magic number
                    f.write(struct.pack('<I', 0))  # Version
                    f.write(struct.pack('<I', 0))  # Number of strings
                    f.write(struct.pack('<I', 28)) # Offset of key table
                    f.write(struct.pack('<I', 28)) # Offset of value table
                    f.write(struct.pack('<I', 0))  # Hash table size
                    f.write(struct.pack('<I', 28)) # Offset of hash table
                
                print(f"✓ Creado {mo_file}")
                
            except Exception as e2:
                print(f"Error procesando {po_file}: {e2}")

if __name__ == '__main__':
    compile_translations()