from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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


class Socio(models.Model):
    MODELO_ESTUDIOS_CHOICES = [
        ('modelo_d', _('Modelo D')),
        ('pai', _('PAI (Programa de Aprendizaje en Inglés)')),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Usuario')
    )
    
    numero_socio = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name=_('Número de socio'),
        help_text=_('Número único de identificación del socio')
    )
    
    fecha_alta = models.DateField(
        auto_now_add=True, 
        verbose_name=_('Fecha de alta')
    )
    
    telefono_1 = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name=_('Teléfono 1'),
        help_text=_('Teléfono principal de contacto')
    )
    
    telefono_2 = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name=_('Teléfono 2'),
        help_text=_('Teléfono secundario de contacto')
    )
    
    activo = models.BooleanField(
        default=True, 
        verbose_name=_('Socio activo'),
        help_text=_('Indica si el socio está actualmente activo')
    )
    
    apellidos_familia = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Apellidos de la familia'),
        help_text=_('Apellidos familiares')
    )
    
    poblacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Población'),
        help_text=_('Ciudad o pueblo de residencia')
    )
    
    direccion = models.TextField(
        blank=True,
        verbose_name=_('Dirección'),
        help_text=_('Dirección del domicilio del socio')
    )
    
    dni = models.CharField(
        max_length=9,
        blank=True,
        verbose_name=_('DNI/NIE'),
        help_text=_('Documento Nacional de Identidad o NIE')
    )
    
    numero_hijos = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('Número de hijos'),
        help_text=_('Cantidad total de hijos')
    )
    
    # Nuevos campos solicitados
    nombre_padre = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Nombre del padre')
    )
    
    nombre_madre = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Nombre de la madre')
    )
    
    correo_contacto_1 = models.EmailField(
        blank=True,
        verbose_name=_('Correo de contacto 1'),
        help_text=_('Email principal de contacto')
    )
    
    correo_contacto_2 = models.EmailField(
        blank=True,
        verbose_name=_('Correo de contacto 2'),
        help_text=_('Email secundario de contacto')
    )
    
    nombre_alumnos = models.TextField(
        blank=True,
        verbose_name=_('Nombre de los alumnos'),
        help_text=_('Nombres de los hijos/alumnos (uno por línea)')
    )
    
    iban = models.CharField(
        max_length=34,
        blank=True,
        verbose_name=_('IBAN'),
        help_text=_('Número de cuenta bancaria (IBAN)')
    )
    
    bic = models.CharField(
        max_length=11,
        blank=True,
        verbose_name=_('BIC/SWIFT'),
        help_text=_('Código BIC/SWIFT del banco')
    )
    
    modelo_estudios = models.CharField(
        max_length=20,
        choices=MODELO_ESTUDIOS_CHOICES,
        blank=True,
        verbose_name=_('Modelo de estudios'),
        help_text=_('Modelo educativo del centro')
    )
    
    class Meta:
        verbose_name = _('Socio')
        verbose_name_plural = _('Socios')
        ordering = ['numero_socio']
    
    def __str__(self):
        nombre_completo = self.user.get_full_name() or self.user.username
        return f"{nombre_completo} - {self.numero_socio}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del socio"""
        return self.user.get_full_name() or self.user.username
    
    def get_alumnos_lista(self):
        """Retorna una lista con los nombres de los alumnos"""
        if self.nombre_alumnos:
            return [nombre.strip() for nombre in self.nombre_alumnos.split('\n') if nombre.strip()]
        return []
    
    def get_modelo_estudios_display_value(self):
        """Retorna el valor legible del modelo de estudios"""
        return dict(self.MODELO_ESTUDIOS_CHOICES).get(self.modelo_estudios, self.modelo_estudios)


class Actividad(models.Model):
    TIPO_ACTIVIDAD_CHOICES = [
        ('taller', _('Taller')),
        ('excursion', _('Excursión')),
        ('reunion', _('Reunión')),
        ('festival', _('Festival')),
        ('evento_social', _('Evento social')),
    ]
    
    fecha = models.DateField(
        verbose_name=_('Fecha'),
        help_text=_('Fecha en la que se realizará la actividad')
    )
    
    titulo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Título'),
        help_text=_('Título de la actividad')
    )
    
    hora_comienzo = models.TimeField(
        verbose_name=_('Hora de comienzo'),
        help_text=_('Hora de inicio de la actividad')
    )
    
    hora_finalizacion = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_('Hora de finalización'),
        help_text=_('Hora de finalización de la actividad (opcional)')
    )
    
    descripcion = models.TextField(
        verbose_name=_('Descripción'),
        help_text=_('Descripción detallada de la actividad')
    )
    
    donde = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Dónde'),
        help_text=_('Lugar donde se realizará la actividad')
    )
    
    imagen = models.ImageField(
        upload_to='actividades/imagenes/',
        blank=True,
        null=True,
        verbose_name=_('Imagen'),
        help_text=_('Imagen representativa de la actividad')
    )
    
    link = models.URLField(
        blank=True,
        verbose_name=_('Enlace'),
        help_text=_('Enlace web relacionado con la actividad (opcional)')
    )
    
    tipo_actividad = models.CharField(
        max_length=20,
        choices=TIPO_ACTIVIDAD_CHOICES,
        verbose_name=_('Tipo de actividad'),
        help_text=_('Categoría de la actividad')
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name=_('Actividad activa'),
        help_text=_('Indica si la actividad está visible y activa')
    )
    
    class Meta:
        verbose_name = _('Actividad')
        verbose_name_plural = _('Actividades')
        ordering = ['fecha', 'hora_comienzo']
    
    def __str__(self):
        titulo = self.titulo or f"{self.get_tipo_actividad_display()} - {self.descripcion[:30]}"
        return f"{titulo} ({self.fecha})"
    
    def get_duracion(self):
        """Retorna la duración de la actividad si tiene hora de finalización"""
        if self.hora_finalizacion:
            from datetime import datetime, timedelta
            inicio = datetime.combine(self.fecha, self.hora_comienzo)
            fin = datetime.combine(self.fecha, self.hora_finalizacion)
            
            # Si la hora de fin es menor que la de inicio, asumimos que es al día siguiente
            if fin < inicio:
                fin += timedelta(days=1)
            
            duracion = fin - inicio
            horas = duracion.seconds // 3600
            minutos = (duracion.seconds % 3600) // 60
            
            if horas > 0:
                return f"{horas}h {minutos}m" if minutos > 0 else f"{horas}h"
            else:
                return f"{minutos}m"
        return None
    
    def get_hora_completa(self):
        """Retorna la hora de inicio y fin si está disponible"""
        if self.hora_finalizacion:
            return f"{self.hora_comienzo.strftime('%H:%M')} - {self.hora_finalizacion.strftime('%H:%M')}"
        return self.hora_comienzo.strftime('%H:%M')
    
    def es_hoy(self):
        """Verifica si la actividad es hoy"""
        from datetime import date
        return self.fecha == date.today()
    
    def es_pasada(self):
        """Verifica si la actividad ya pasó"""
        from datetime import date
        return self.fecha < date.today()


class ConcursoDibujo(models.Model):
    """Modelo para almacenar participaciones del concurso navideño"""
    CURSO_CHOICES = [
        ('3_anos', _('3 años')),
        ('4_anos', _('4 años')),
        ('5_anos', _('5 años')),
        ('1_primaria', _('1º Primaria')),
        ('2_primaria', _('2º Primaria')),
        ('3_primaria', _('3º Primaria')),
        ('4_primaria', _('4º Primaria')),
        ('5_primaria', _('5º Primaria')),
        ('6_primaria', _('6º Primaria')),
    ]
    
    socio = models.ForeignKey('Socio', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Socio'))
    nombre_nino = models.CharField(max_length=200, verbose_name=_('Nombre del niño'))
    curso = models.CharField(max_length=50, choices=CURSO_CHOICES, verbose_name=_('Curso'))
    email = models.EmailField(verbose_name=_('Email de contacto'))
    imagen = models.ImageField(upload_to='concurso_navidad/', verbose_name=_('Fotografía del dibujo'))
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de envío'))
    aceptado = models.BooleanField(default=False, verbose_name=_('Dibujo aceptado'))

    class Meta:
        verbose_name = _('Participación concurso')
        verbose_name_plural = _('Participaciones concurso')
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.nombre_nino} ({self.curso}) - {self.fecha_envio.strftime('%d/%m/%Y') if self.fecha_envio else ''}"


class Noticia(models.Model):
    """Modelo para las noticias de la APYMA"""
    
    titulo = models.CharField(
        max_length=200,
        verbose_name=_('Título')
    )
    
    titulo_eu = models.CharField(
        max_length=200,
        verbose_name=_('Título (Euskera)'),
        help_text=_('Título en euskera')
    )
    
    resumen = models.TextField(
        max_length=300,
        verbose_name=_('Resumen'),
        help_text=_('Breve descripción que aparecerá en la lista de noticias')
    )
    
    resumen_eu = models.TextField(
        max_length=300,
        verbose_name=_('Resumen (Euskera)'),
        help_text=_('Resumen en euskera')
    )
    
    contenido = models.TextField(
        verbose_name=_('Contenido completo')
    )
    
    contenido_eu = models.TextField(
        verbose_name=_('Contenido completo (Euskera)'),
        help_text=_('Contenido completo en euskera')
    )
    
    imagen = models.ImageField(
        upload_to='noticias/',
        blank=True,
        null=True,
        verbose_name=_('Imagen destacada'),
        help_text=_('Imagen opcional para la noticia')
    )
    
    fecha_publicacion = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Fecha de publicación'),
        help_text=_('Fecha en que se publicará la noticia')
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última modificación')
    )
    
    publicada = models.BooleanField(
        default=True,
        verbose_name=_('Publicada'),
        help_text=_('Si está marcado, la noticia será visible para todos')
    )
    
    destacada = models.BooleanField(
        default=False,
        verbose_name=_('Noticia destacada'),
        help_text=_('Las noticias destacadas aparecen primero')
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL amigable'),
        help_text=_('Se genera automáticamente del título')
    )
    
    class Meta:
        verbose_name = _('Noticia')
        verbose_name_plural = _('Noticias')
        ordering = ['-destacada', '-fecha_publicacion']
    
    def __str__(self):
        return self.titulo
    
    def get_titulo_localized(self, language='es'):
        """Obtiene el título en el idioma especificado"""
        if language == 'eu':
            return self.titulo_eu
        return self.titulo
    
    def get_resumen_localized(self, language='es'):
        """Obtiene el resumen en el idioma especificado"""
        if language == 'eu':
            return self.resumen_eu
        return self.resumen
    
    def get_contenido_localized(self, language='es'):
        """Obtiene el contenido en el idioma especificado"""
        if language == 'eu':
            return self.contenido_eu
        return self.contenido
    
    def save(self, *args, **kwargs):
        """Genera el slug automáticamente si no existe"""
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.titulo)
            slug = base_slug
            counter = 1
            
            while Noticia.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)


class ConsejoEducativo(models.Model):
    """Modelo para consejos educativos con páginas HTML independientes"""
    titulo = models.CharField(
        max_length=200,
        verbose_name=_('Título'),
        help_text=_('Título del consejo educativo')
    )
    
    titulo_eu = models.CharField(
        max_length=200,
        verbose_name=_('Título (Euskera)'),
        help_text=_('Título en euskera'),
        blank=True,
        null=True
    )
    
    descripcion = models.TextField(
        verbose_name=_('Descripción corta'),
        help_text=_('Breve descripción que aparece en la tarjeta')
    )
    
    descripcion_eu = models.TextField(
        verbose_name=_('Descripción corta (Euskera)'),
        help_text=_('Descripción en euskera'),
        blank=True,
        null=True
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL amigable'),
        help_text=_('Se genera automáticamente del título')
    )
    
    archivo_html = models.CharField(
        max_length=500,
        verbose_name=_('Ruta del archivo HTML'),
        help_text=_('Ruta relativa desde media/consejos/, ej: habitos-estudio.html')
    )
    
    imagen = models.ImageField(
        upload_to='consejos/',
        verbose_name=_('Imagen de portada'),
        help_text=_('Imagen que aparece en la tarjeta'),
        blank=True,
        null=True
    )
    
    fecha_publicacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de publicación')
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última modificación')
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name=_('Activo'),
        help_text=_('Solo los consejos activos son visibles')
    )
    
    orden = models.IntegerField(
        default=0,
        verbose_name=_('Orden'),
        help_text=_('Orden de aparición (menor número aparece primero)')
    )
    
    class Meta:
        verbose_name = _('Consejo Educativo')
        verbose_name_plural = _('Consejos Educativos')
        ordering = ['orden', '-fecha_publicacion']
    
    def __str__(self):
        return self.titulo
    
    def get_titulo_localized(self, language='es'):
        """Obtiene el título en el idioma especificado"""
        if language == 'eu' and self.titulo_eu:
            return self.titulo_eu
        return self.titulo
    
    def get_descripcion_localized(self, language='es'):
        """Obtiene la descripción en el idioma especificado"""
        if language == 'eu' and self.descripcion_eu:
            return self.descripcion_eu
        return self.descripcion
    
    def save(self, *args, **kwargs):
        """Genera el slug automáticamente si no existe"""
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.titulo)
            slug = base_slug
            counter = 1
            
            while ConsejoEducativo.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)
