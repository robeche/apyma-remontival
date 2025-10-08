#!/usr/bin/env python3
import os
import polib

def compile_po_to_mo():
    """Convierte archivo .po a .mo usando polib"""
    po_file_path = r'x:\Proyectos\ApymaRemontival\locale\eu\LC_MESSAGES\django.po'
    mo_file_path = r'x:\Proyectos\ApymaRemontival\locale\eu\LC_MESSAGES\django.mo'
    
    try:
        # Cargar el archivo .po
        po = polib.pofile(po_file_path)
        
        # Compilar a .mo
        po.save_as_mofile(mo_file_path)
        
        print(f"✓ Compilado exitosamente: {mo_file_path}")
        
    except Exception as e:
        print(f"✗ Error al compilar: {e}")

if __name__ == "__main__":
    compile_po_to_mo()