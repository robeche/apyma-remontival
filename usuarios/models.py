from django.db import models
from django.utils.translation import gettext_lazy as _

class Contacto(models.Model):
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
    
    nombre_apellidos = models.CharField(
        max_length=200,
        verbose_name=_('Nombre y apellidos')
    )
    
    asunto = models.CharField(
        max_length=50,
        choices=ASUNTOS_CHOICES,
        verbose_name=_('Asunto relacionado')
    )
    
    mensaje = models.TextField(
        verbose_name=_('Mensaje')
    )
    
    email_contacto = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email de contacto'),
        help_text=_('Opcional: para poder responderte')
    )
    
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de envío')
    )
    
    respondido = models.BooleanField(
        default=False,
        verbose_name=_('Respondido')
    )
    
    notas_internas = models.TextField(
        blank=True,
        verbose_name=_('Notas internas'),
        help_text=_('Para uso interno de la Apyma')
    )
    
    class Meta:
        verbose_name = _('Mensaje de contacto')
        verbose_name_plural = _('Mensajes de contacto')
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"{self.nombre_apellidos} - {self.get_asunto_display()} ({self.fecha_envio.strftime('%d/%m/%Y')})"
    
    def get_asunto_display_value(self):
        """Retorna el valor legible del asunto"""
        return dict(self.ASUNTOS_CHOICES).get(self.asunto, self.asunto)
