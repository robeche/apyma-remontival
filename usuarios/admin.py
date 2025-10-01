from django.contrib import admin
from .models import Contacto, Socio, Actividad

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellidos', 'asunto', 'email_contacto', 'fecha_envio', 'respondido')
    list_filter = ('asunto', 'respondido', 'fecha_envio')
    search_fields = ('nombre_apellidos', 'email_contacto', 'mensaje')
    readonly_fields = ('fecha_envio',)
    list_editable = ('respondido',)

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('numero_socio', 'get_nombre_completo', 'apellidos_familia', 'telefono_1', 'poblacion', 'activo', 'modelo_estudios', 'fecha_alta')
    list_filter = ('activo', 'modelo_estudios', 'fecha_alta', 'poblacion')
    search_fields = ('numero_socio', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'apellidos_familia', 'nombre_padre', 'nombre_madre', 'poblacion')
    readonly_fields = ('fecha_alta',)
    list_editable = ('activo',)
    
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'numero_socio', 'fecha_alta', 'activo')
        }),
        ('Datos personales', {
            'fields': ('apellidos_familia', 'dni', 'poblacion', 'direccion')
        }),
        ('Contacto', {
            'fields': ('telefono_1', 'telefono_2', 'correo_contacto_1', 'correo_contacto_2')
        }),
        ('Información familiar', {
            'fields': ('nombre_padre', 'nombre_madre', 'numero_hijos', 'nombre_alumnos', 'modelo_estudios')
        }),
        ('Datos bancarios', {
            'fields': ('iban', 'bic'),
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre completo'


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('descripcion_corta', 'fecha', 'get_hora_completa', 'tipo_actividad', 'activa', 'fecha_creacion')
    list_filter = ('tipo_actividad', 'activa', 'fecha', 'fecha_creacion')
    search_fields = ('descripcion', 'donde', 'tipo_actividad')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    list_editable = ('activa',)
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('descripcion', 'donde', 'tipo_actividad', 'activa')
        }),
        ('Fecha y hora', {
            'fields': ('fecha', 'hora_comienzo', 'hora_finalizacion')
        }),
        ('Contenido adicional', {
            'fields': ('imagen', 'link'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
