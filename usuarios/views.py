from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.cache import cache_control
from .forms import ContactoForm, ActividadForm
from .models import Contacto, Actividad
import os
import mimetypes

def debug_admin_user(request):
    """Vista temporal para debuggear usuario admin"""
    from django.contrib.auth.models import User
    
    info = []
    
    # Listar todos los usuarios
    users = User.objects.all()
    info.append(f"Total usuarios: {users.count()}")
    
    for user in users:
        info.append(f"Usuario: {user.username}")
        info.append(f"  - Email: {user.email}")
        info.append(f"  - is_active: {user.is_active}")
        info.append(f"  - is_staff: {user.is_staff}")
        info.append(f"  - is_superuser: {user.is_superuser}")
        info.append(f"  - last_login: {user.last_login}")
        info.append("---")
    
    return HttpResponse("<br>".join(info))

def admin_login_view(request):
    """Vista de login personalizada para admin que evita LOGIN_REDIRECT_URL"""
    from django.contrib.auth import authenticate, login as auth_login
    from django.contrib.admin.forms import AdminAuthenticationForm
    
    if request.method == 'POST':
        form = AdminAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_active and user.is_staff:
                auth_login(request, user)
                # Redirigir directamente al admin, ignorando LOGIN_REDIRECT_URL
                return redirect('/admin/')
    else:
        form = AdminAuthenticationForm(request)
    
    return render(request, 'admin/login.html', {'form': form})

def home(request):
    """Página de inicio pública con información de la Apyma"""
    return render(request, 'usuarios/home.html')

@login_required
def dashboard(request):
    return render(request, 'usuarios/dashboard.html')

def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('dashboard')
	else:
		form = UserCreationForm()
	return render(request, 'usuarios/register.html', {'form': form})

def contacto(request):
	"""Vista para el formulario de contacto con la Apyma"""
	if request.method == 'POST':
		form = ContactoForm(request.POST)
		if form.is_valid():
			# Extraer datos del formulario
			nombre = form.cleaned_data['nombre_apellidos']
			asunto = form.cleaned_data['asunto']
			email_contacto = form.cleaned_data.get('email_contacto', '')
			mensaje = form.cleaned_data['mensaje']
			
			# Guardar en base de datos
			contacto_obj = Contacto.objects.create(
				nombre_apellidos=nombre,
				asunto=asunto,
				email_contacto=email_contacto,
				mensaje=mensaje
			)
			
			# Enviar email a la Apyma
			try:
				asunto_legible = contacto_obj.get_asunto_display_value()
				
				# Crear el contenido del email
				email_subject = f"Nuevo mensaje de contacto: {asunto_legible}"
				email_body = f"""
Nuevo mensaje recibido a través del formulario de contacto:

DATOS DEL REMITENTE:
- Nombre: {nombre}
- Email: {email_contacto if email_contacto else 'No proporcionado'}
- Asunto: {asunto_legible}

MENSAJE:
{mensaje}

---
Enviado desde el sitio web de la Apyma Remontival
Fecha: {contacto_obj.fecha_envio.strftime('%d/%m/%Y a las %H:%M')}
ID del mensaje: {contacto_obj.id}
				"""
				
				send_mail(
					email_subject,
					email_body,
					settings.DEFAULT_FROM_EMAIL,
					[settings.CONTACT_EMAIL],
					fail_silently=False,
				)
				
				messages.success(request, _('¡Gracias por contactarnos! Hemos recibido tu mensaje y te responderemos pronto.'))
				
			except Exception as e:
				# Si falla el envío del email, pero se guardó en BD
				messages.warning(request, _('Tu mensaje se ha guardado correctamente, pero hubo un problema al enviar la notificación. Nos pondremos en contacto contigo pronto.'))
				print(f"Error enviando email: {e}")  # Para debug
			
			return redirect('contacto')
	else:
		form = ContactoForm()
	
	return render(request, 'usuarios/contacto.html', {'form': form})


def logout_view(request):
    """Vista personalizada para cerrar sesión"""
    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username
        logout(request)
        messages.success(request, _('Has cerrado sesión correctamente, {}. ¡Hasta pronto!').format(username))
    return redirect('home')


def actividades(request):
    """Vista para mostrar el calendario de actividades"""
    from datetime import datetime, timedelta
    import calendar
    import json
    
    # Obtener el mes y año actual o desde los parámetros GET
    today = datetime.now()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Calcular mes anterior y siguiente para navegación
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Crear el calendario del mes
    cal = calendar.Calendar(firstweekday=0)  # Lunes como primer día
    month_days = cal.monthdays2calendar(year, month)
    
    # Obtener actividades reales de la base de datos para el mes actual
    from datetime import date
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Consultar actividades del mes
    actividades_mes = Actividad.objects.filter(
        fecha__gte=first_day,
        fecha__lte=last_day,
        activa=True
    ).order_by('fecha', 'hora_comienzo')
    
    # Organizar actividades por día
    actividades_por_dia = {}
    for actividad in actividades_mes:
        dia = actividad.fecha.day
        if dia not in actividades_por_dia:
            actividades_por_dia[dia] = []
        
        actividades_por_dia[dia].append({
            'id': actividad.id,
            'titulo': f"{actividad.get_tipo_actividad_display()}",
            'hora': actividad.hora_comienzo.strftime('%H:%M'),
            'hora_fin': actividad.hora_finalizacion.strftime('%H:%M') if actividad.hora_finalizacion else None,
            'tipo': actividad.tipo_actividad,
            'descripcion': actividad.descripcion,
            'donde': actividad.donde,
            'link': actividad.link,
            'imagen_url': actividad.imagen.url if actividad.imagen else ''
        })
    
    # Convertir actividades a formato JSON para JavaScript
    actividades_json = {}
    for dia, lista_actividades in actividades_por_dia.items():
        key = f"{year},{month},{dia}"
        actividades_json[key] = lista_actividades
    
    # Crear formulario para nuevas actividades (solo para staff)
    form = None
    if request.user.is_staff:
        form = ActividadForm()
    
    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_days': month_days,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'today': today,
        'actividades': actividades_por_dia,
        'actividades_json': json.dumps(actividades_json),
        'weekday_names': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
        'form': form,
        'is_staff': request.user.is_staff
    }
    
    return render(request, 'usuarios/actividades.html', context)


@login_required
@require_POST
def crear_actividad(request):
    """Vista para crear una nueva actividad via AJAX (solo staff)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para crear actividades'})
    
    form = ActividadForm(request.POST, request.FILES)
    if form.is_valid():
        actividad = form.save()
        return JsonResponse({
            'success': True, 
            'message': 'Actividad creada exitosamente',
            'actividad': {
                'id': actividad.id,
                'fecha': actividad.fecha.strftime('%Y-%m-%d'),
                'titulo': actividad.get_tipo_actividad_display(),
                'hora': actividad.hora_comienzo.strftime('%H:%M'),
                'descripcion': actividad.descripcion
            }
        })
    else:
        errors = {}
        for field, field_errors in form.errors.items():
            errors[field] = field_errors
        return JsonResponse({'success': False, 'errors': errors})


@login_required
def detalle_actividad(request, actividad_id):
    """Vista para obtener los detalles de una actividad via AJAX"""
    try:
        actividad = Actividad.objects.get(id=actividad_id, activa=True)
        
        return JsonResponse({
            'success': True,
            'actividad': {
                'id': actividad.id,
                'fecha': actividad.fecha.strftime('%d/%m/%Y'),
                'fecha_iso': actividad.fecha.strftime('%Y-%m-%d'),
                'hora_comienzo': actividad.hora_comienzo.strftime('%H:%M'),
                'hora_finalizacion': actividad.hora_finalizacion.strftime('%H:%M') if actividad.hora_finalizacion else None,
                'hora_completa': actividad.get_hora_completa(),
                'duracion': actividad.get_duracion(),
                'tipo_actividad': actividad.tipo_actividad,
                'tipo_actividad_display': actividad.get_tipo_actividad_display(),
                'descripcion': actividad.descripcion,
                'donde': actividad.donde,
                'link': actividad.link,
                'imagen_url': actividad.imagen.url if actividad.imagen else None,
                'es_hoy': actividad.es_hoy(),
                'es_pasada': actividad.es_pasada()
            },
            'is_staff': request.user.is_staff
        })
        
    except Actividad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Actividad no encontrada'})


@login_required
@require_POST
def actualizar_actividad(request, actividad_id):
    """Vista para actualizar una actividad via AJAX (solo staff)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para editar actividades'})
    
    try:
        actividad = Actividad.objects.get(id=actividad_id, activa=True)
        form = ActividadForm(request.POST, request.FILES, instance=actividad)
        
        if form.is_valid():
            actividad_actualizada = form.save()
            return JsonResponse({
                'success': True, 
                'message': 'Actividad actualizada exitosamente',
                'actividad': {
                    'id': actividad_actualizada.id,
                    'fecha': actividad_actualizada.fecha.strftime('%Y-%m-%d'),
                    'titulo': actividad_actualizada.get_tipo_actividad_display(),
                    'hora': actividad_actualizada.hora_comienzo.strftime('%H:%M'),
                    'descripcion': actividad_actualizada.descripcion
                }
            })
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = field_errors
            return JsonResponse({'success': False, 'errors': errors})
            
    except Actividad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Actividad no encontrada'})


@login_required
@require_POST
def eliminar_actividad(request, actividad_id):
    """Vista para eliminar una actividad via AJAX (solo staff)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar actividades'})
    
    try:
        actividad = Actividad.objects.get(id=actividad_id, activa=True)
        
        # En lugar de eliminar completamente, marcamos como inactiva
        actividad.activa = False
        actividad.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Actividad eliminada exitosamente'
        })
        
    except Actividad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Actividad no encontrada'})

def comedor(request):
    """Vista para mostrar información del comedor escolar"""
    # Información simplificada del comedor
    menu_info = {
        'mes_actual': 'Septiembre 2025',
        'empresa': 'El Gusto de Crecer',
        'descripcion': 'Empresa especializada en catering escolar con más de 15 años de experiencia. Elaboramos menús equilibrados y adaptados a las necesidades nutricionales de los escolares.',
        'contacto_empresa': {
            'nombre': 'El Gusto de Crecer',
            'telefono': '986 123 456',
            'email': 'info@elgustodecrecer.es',
            'web': 'www.elgustodecrecer.es'
        },
        'menus_disponibles': [
            {
                'titulo': 'Menú Septiembre 2025 (Castellano)',
                'archivo': 'menu_septiembre_castellano.pdf',
                'idioma': 'Castellano'
            },
            {
                'titulo': 'Menú Septiembre 2025 (Euskera)',
                'archivo': 'menu_septiembre_euskera.pdf',
                'idioma': 'Euskera'
            }
        ]
    }
    
    return render(request, 'usuarios/comedor.html', {'menu_info': menu_info})

@xframe_options_exempt
@cache_control(max_age=3600)  # Cache por 1 hora
def serve_pdf(request, filename):
    """Vista personalizada para servir PDFs sin restricciones de X-Frame-Options"""
    # Verificar que el archivo tenga extensión PDF
    if not filename.endswith('.pdf'):
        raise Http404("Archivo no encontrado")
    
    # Construir la ruta completa del archivo
    file_path = os.path.join(settings.MEDIA_ROOT, 'comedor', filename)
    
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        raise Http404("Archivo no encontrado")
    
    # Verificar que el archivo está dentro del directorio permitido (seguridad)
    allowed_dir = os.path.join(settings.MEDIA_ROOT, 'comedor')
    if not os.path.commonpath([file_path, allowed_dir]) == allowed_dir:
        raise Http404("Acceso denegado")
    
    try:
        with open(file_path, 'rb') as pdf_file:
            content = pdf_file.read()
        
        # Crear respuesta HTTP con el contenido del PDF
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        # Importante: NO establecer X-Frame-Options para permitir iframe
        # El decorador @xframe_options_exempt ya se encarga de esto
        
        return response
        
    except Exception as e:
        raise Http404("Error al leer el archivo")


def simple_set_language(request):
    """Vista simple que REEMPLAZA a /i18n/setlang/"""
    if request.method == 'POST':
        language = request.POST.get('language', 'es')
        
        # Validar idioma
        if language not in ['es', 'eu']:
            language = 'es'
        
        # Crear HTML con JavaScript para redirección Y establecer cookie
        redirect_url = f'/{language}/'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Redirigiendo...</title>
        </head>
        <body>
            <p>Cambiando idioma...</p>
            <script>
                // Establecer cookie de idioma
                document.cookie = "django_language={language}; path=/; max-age=31536000; SameSite=Lax";
                // Redirigir inmediatamente
                window.location.replace('{redirect_url}');
            </script>
        </body>
        </html>
        """
        
        response = HttpResponse(html)
        
        # También establecer cookie desde el servidor por si acaso
        response.set_cookie(
            'django_language',
            language,
            max_age=365 * 24 * 60 * 60,  # 1 año
            path='/',
            secure=False,  # Temporal para que funcione
            httponly=False,  # Permitir acceso desde JavaScript
            samesite='Lax'
        )
        
        return response
    
    # Si no es POST, redirigir a home español
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect('/es/')


def debug_redirect(request):
    """Vista de debug para probar redirecciones simples"""
    if request.method == 'POST':
        language = request.POST.get('language', 'NO_LANGUAGE_FOUND')
        
        # Simple debug info sin objetos complejos
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debug POST Result</title>
        </head>
        <body>
            <h2>POST recibido!</h2>
            <h3>Datos basicos:</h3>
            <p><strong>Metodo:</strong> {request.method}</p>
            <p><strong>Idioma recibido:</strong> {language}</p>
            <p><strong>Path:</strong> {request.path}</p>
            <p><strong>Host:</strong> {request.get_host()}</p>
            <p><strong>HTTPS:</strong> {request.is_secure()}</p>
            
            <h3>POST data completo:</h3>
            <ul>
        """
        
        for key, value in request.POST.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        
        html += f"""
            </ul>
            
            <h3>Pruebas manuales:</h3>
            <p><a href="/es/">Ir a /es/ manualmente</a></p>
            <p><a href="/eu/">Ir a /eu/ manualmente</a></p>
            <p><a href="/debug-redirect/">Volver al formulario</a></p>
        </body>
        </html>
        """
        
        return HttpResponse(html)
    
    # GET request - show form
    try:
        from django.middleware.csrf import get_token
        csrf_token = get_token(request)
    except:
        csrf_token = "ERROR_GETTING_TOKEN"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Language Selector</title>
    </head>
    <body>
        <h2>Debug Language Selector</h2>
        <p>Selecciona un idioma y veremos que pasa:</p>
        <form method="post">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            <label>
                <input type="radio" name="language" value="es" checked> Español
            </label><br>
            <label>
                <input type="radio" name="language" value="eu"> Euskera  
            </label><br><br>
            <button type="submit">Cambiar idioma</button>
        </form>
        
        <h3>Info actual:</h3>
        <p>Path: {request.get_full_path()}</p>
        <p>Host: {request.get_host()}</p>
        <p>HTTPS: {request.is_secure()}</p>
    </body>
    </html>
    """
    
    return HttpResponse(html)
