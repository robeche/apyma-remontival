from django import forms
from django.core.exceptions import ValidationError
import os

class MenuUploadForm(forms.Form):
    """Formulario para subir menús del comedor"""
    
    MONTH_CHOICES = [
        ('enero', 'Enero'),
        ('febrero', 'Febrero'),
        ('marzo', 'Marzo'),
        ('abril', 'Abril'),
        ('mayo', 'Mayo'),
        ('junio', 'Junio'),
        ('julio', 'Julio'),
        ('agosto', 'Agosto'),
        ('septiembre', 'Septiembre'),
        ('octubre', 'Octubre'),
        ('noviembre', 'Noviembre'),
        ('diciembre', 'Diciembre'),
    ]
    
    mes = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label='Mes del menú',
        help_text='Selecciona el mes correspondiente al menú'
    )
    
    menu_castellano = forms.FileField(
        label='Menú en Castellano (PDF)',
        help_text='Archivo PDF del menú en castellano',
        required=False
    )
    
    menu_euskera = forms.FileField(
        label='Menú en Euskera (PDF)',
        help_text='Archivo PDF del menú en euskera',
        required=False
    )
    
    menu_completo = forms.FileField(
        label='Menú Completo (PDF - 2 páginas)',
        help_text='Archivo PDF con ambos idiomas (se separará automáticamente)',
        required=False
    )
    
    sobrescribir = forms.BooleanField(
        label='Sobrescribir archivos existentes',
        required=False,
        initial=False,
        help_text='Marcar si quieres reemplazar menús existentes del mismo mes'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        menu_castellano = cleaned_data.get('menu_castellano')
        menu_euskera = cleaned_data.get('menu_euskera')
        menu_completo = cleaned_data.get('menu_completo')
        
        # Al menos uno debe estar presente
        if not menu_castellano and not menu_euskera and not menu_completo:
            raise ValidationError(
                'Debes subir al menos un archivo: menús separados o menú completo.'
            )
        
        # Validar archivos PDF
        for field_name, file_field in [
            ('menu_castellano', menu_castellano),
            ('menu_euskera', menu_euskera),
            ('menu_completo', menu_completo)
        ]:
            if file_field:
                if not file_field.name.lower().endswith('.pdf'):
                    raise ValidationError(f'El archivo {field_name} debe ser un PDF.')
                
                # Validar tamaño (máximo 10MB)
                if file_field.size > 10 * 1024 * 1024:
                    raise ValidationError(f'El archivo {field_name} es demasiado grande (máximo 10MB).')
        
        return cleaned_data