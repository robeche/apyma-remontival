from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Actividad, Noticia

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


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['fecha', 'hora_comienzo', 'hora_finalizacion', 'descripcion', 'donde', 'imagen', 'link', 'tipo_actividad']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora_comienzo': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_finalizacion': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Describe la actividad...')
            }),
            'donde': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Lugar donde se realizará')
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('https://...')
            }),
            'tipo_actividad': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer hora_finalizacion opcional en el formulario
        self.fields['hora_finalizacion'].required = False
        self.fields['donde'].required = False
        self.fields['imagen'].required = False
        self.fields['link'].required = False


class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'titulo_eu', 'resumen', 'resumen_eu', 'contenido', 'contenido_eu', 'imagen', 'publicada']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Título en español')
            }),
            'titulo_eu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Título en euskera')
            }),
            'resumen': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Resumen en español')
            }),
            'resumen_eu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Resumen en euskera')
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': _('Contenido completo en español')
            }),
            'contenido_eu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': _('Contenido completo en euskera')
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'publicada': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos opcionales
        self.fields['titulo_eu'].required = False
        self.fields['resumen_eu'].required = False
        self.fields['contenido_eu'].required = False
        self.fields['imagen'].required = False