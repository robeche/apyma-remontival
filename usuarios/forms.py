from django import forms
from django.utils.translation import gettext_lazy as _

class ContactoForm(forms.Form):
    ASUNTOS_CHOICES = [
        ('informacion_general', _('Información general')),
        ('extraescolares', _('Extraescolares')),
        ('aula_matinal', _('Aula matinal')),
        ('actividades_eventos', _('Actividades y eventos')),
        ('apoyo_educativo', _('Apoyo educativo')),
        ('participacion_familiar', _('Participación familiar')),
        ('sugerencias', _('Sugerencias')),
        ('quejas', _('Quejas o reclamaciones')),
        ('otros', _('Otros')),
    ]
    
    nombre_apellidos = forms.CharField(
        max_length=200,
        label=_('Nombre y apellidos'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Introduce tu nombre completo'),
        })
    )
    
    asunto = forms.ChoiceField(
        choices=ASUNTOS_CHOICES,
        label=_('Asunto relacionado'),
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    email_contacto = forms.EmailField(
        required=False,
        label=_('Tu email (opcional)'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('tu.email@ejemplo.com'),
        }),
        help_text=_('Para poder responderte directamente')
    )
    
    mensaje = forms.CharField(
        label=_('Mensaje'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': _('Escribe tu mensaje aquí...'),
        })
    )
    
    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje')
        if len(mensaje) < 10:
            raise forms.ValidationError(_('El mensaje debe tener al menos 10 caracteres.'))
        return mensaje