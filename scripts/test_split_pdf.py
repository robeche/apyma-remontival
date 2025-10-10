#!/usr/bin/env python
"""
Script para probar la separación de PDFs ya descargados
"""

import os
import sys
from pypdf import PdfReader, PdfWriter

def split_existing_pdf():
    """Separa un PDF existente en castellano y euskera"""
    
    # Directorio de menús
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    media_dir = os.path.join(base_dir, 'media', 'comedor')
    
    # Buscar PDFs de menús
    pdf_files = [f for f in os.listdir(media_dir) if f.endswith('.pdf') and 'octubre' in f.lower()]
    
    if not pdf_files:
        print("❌ No se encontraron PDFs de octubre para separar")
        return
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(media_dir, pdf_file)
        
        print(f"📄 Procesando: {pdf_file}")
        
        try:
            # Leer el PDF
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            
            print(f"   Total de páginas: {total_pages}")
            
            if total_pages < 2:
                print(f"⚠️ El PDF solo tiene {total_pages} página(s), no se puede separar")
                continue
            
            # Crear PDF para castellano (primera página)
            castellano_filename = "menu_octubre_castellano.pdf"
            castellano_path = os.path.join(media_dir, castellano_filename)
            
            writer_castellano = PdfWriter()
            writer_castellano.add_page(reader.pages[0])
            
            with open(castellano_path, 'wb') as output_file:
                writer_castellano.write(output_file)
            
            print(f"✅ Creado: {castellano_filename}")
            
            # Crear PDF para euskera (segunda página)
            euskera_filename = "menu_octubre_euskera.pdf"
            euskera_path = os.path.join(media_dir, euskera_filename)
            
            writer_euskera = PdfWriter()
            writer_euskera.add_page(reader.pages[1])
            
            with open(euskera_path, 'wb') as output_file:
                writer_euskera.write(output_file)
            
            print(f"✅ Creado: {euskera_filename}")
            
            # Si hay más páginas, crear un PDF con todas las páginas adicionales
            if total_pages > 2:
                extra_filename = "menu_octubre_adicional.pdf"
                extra_path = os.path.join(media_dir, extra_filename)
                
                writer_extra = PdfWriter()
                for page_num in range(2, total_pages):
                    writer_extra.add_page(reader.pages[page_num])
                
                with open(extra_path, 'wb') as output_file:
                    writer_extra.write(output_file)
                
                print(f"✅ Creado: {extra_filename} (páginas adicionales)")
            
            print(f"🎉 PDF separado exitosamente!")
            
        except Exception as e:
            print(f"❌ Error procesando {pdf_file}: {e}")

if __name__ == "__main__":
    split_existing_pdf()