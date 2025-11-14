#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para compilar manualmente el archivo django.po a django.mo
"""
import os
import sys

# Configurar el path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings')

try:
    import django
    django.setup()
    
    from django.core.management import call_command
    
    print("Compilando traducciones de euskera...")
    call_command('compilemessages', locale=['eu'], verbosity=2, ignore_patterns=[])
    print("\n✓ Traducciones compiladas exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
