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
from .forms import ContactoForm, ActividadForm, NoticiaForm
from .models import Contacto, Actividad, Noticia
import os
import mimetypes
from datetime import datetime

def admin_redirect_view(request):
    """Redirigir admin a pythonanywhere donde funciona"""
    # Construir la URL completa manteniendo el path
    path = request.get_full_path()
    redirect_url = f"https://robeche.pythonanywhere.com{path}"
    return redirect(redirect_url)

def debug_login(request):
    """Vista para debuggear el proceso de login"""
    from django.contrib.auth import authenticate
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        info = []
        info.append(f"<h2>Login Debug - POST</h2>")
        info.append(f"Username received: '{username}'<br>")
        info.append(f"Password length: {len(password) if password else 0}<br>")
        
        # Intentar autenticación
        user = authenticate(request, username=username, password=password)
        info.append(f"Authentication result: {user}<br>")
        
        if user:
            info.append(f"User is active: {user.is_active}<br>")
            info.append(f"User is staff: {user.is_staff}<br>")
            info.append(f"User is superuser: {user.is_superuser}<br>")
            
            # Intentar login
            from django.contrib.auth import login as auth_login
            try:
                auth_login(request, user)
                info.append(f"Login successful!<br>")
                info.append(f"User is authenticated now: {request.user.is_authenticated}<br>")
                info.append(f"Session key: {request.session.session_key}<br>")
            except Exception as e:
                info.append(f"Login failed with error: {e}<br>")
        else:
            info.append("Authentication failed - check username/password<br>")
        
        info.append("<br><a href='/es/debug-login/'>Try again</a><br>")
        info.append("<a href='/es/debug-headers/'>Check headers</a>")
        
        return HttpResponse("".join(info))
    
    # GET request - show form
    html = """
    <h2>Debug Login Form</h2>
    <form method="post">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        <label>Username:</label><br>
        <input type="text" name="username" required><br><br>
        <label>Password:</label><br>
        <input type="password" name="password" required><br><br>
        <input type="submit" value="Test Login">
    </form>
    <br><a href="/es/debug-headers/">Check headers</a>
    """.format(csrf_token=request.META.get('CSRF_COOKIE', ''))
    
    return HttpResponse(html)

def test_session(request):
    """Vista temporal para probar creación de sesiones"""
    # Forzar creación de sesión
    request.session['test_key'] = 'test_value'
    request.session.save()
    
    info = []
    info.append(f"<h2>Session Test</h2>")
    info.append(f"Session key after save: {request.session.session_key}<br>")
    info.append(f"Session test_key: {request.session.get('test_key', 'NOT FOUND')}<br>")
    info.append(f"Session is empty: {request.session.is_empty()}<br>")
    info.append(f"Host: {request.get_host()}<br>")
    info.append("<br><a href='/es/debug-headers/'>Ver debug headers</a>")
    
    return HttpResponse("".join(info))

def debug_headers_cookies(request):
    """Vista para debuggear headers y cookies en producción"""
    info = []
    
    # Información básica de la request
    info.append(f"<h2>Request Info</h2>")
    info.append(f"Host: {request.get_host()}")
    info.append(f"Full path: {request.get_full_path()}")
    info.append(f"Is secure: {request.is_secure()}")
    info.append(f"Method: {request.method}")
    info.append("<br>")
    
    # Headers importantes
    info.append(f"<h2>Headers</h2>")
    important_headers = [
        'HTTP_HOST', 'HTTP_X_FORWARDED_HOST', 'HTTP_X_ORIGINAL_HOST', 
        'HTTP_X_FORWARDED_PROTO', 'HTTP_X_FORWARDED_FOR',
        'HTTP_COOKIE', 'HTTP_USER_AGENT'
    ]
    
    for header in important_headers:
        value = request.META.get(header, 'NOT SET')
        info.append(f"{header}: {value}<br>")
    
    # Cookies de la request
    info.append(f"<h2>Request Cookies</h2>")
    for key, value in request.COOKIES.items():
        info.append(f"{key}: {value}<br>")
    
    # Información de sesión
    info.append(f"<h2>Session Info</h2>")
    info.append(f"Session key: {request.session.session_key}<br>")
    info.append(f"Session is empty: {request.session.is_empty()}<br>")
    info.append(f"Session items: {dict(request.session)}<br>")
    
    # Usuario
    info.append(f"<h2>User Info</h2>")
    info.append(f"Is authenticated: {request.user.is_authenticated}<br>")
    if request.user.is_authenticated:
        info.append(f"Username: {request.user.username}<br>")
        info.append(f"Is staff: {request.user.is_staff}<br>")
    
    # Configuración de Django
    from django.conf import settings
    info.append(f"<h2>Django Settings</h2>")
    info.append(f"SESSION_COOKIE_NAME: {getattr(settings, 'SESSION_COOKIE_NAME', 'NOT SET')}<br>")
    info.append(f"SESSION_COOKIE_DOMAIN: {getattr(settings, 'SESSION_COOKIE_DOMAIN', 'NOT SET')}<br>")
    info.append(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'NOT SET')}<br>")
    info.append(f"USE_X_FORWARDED_HOST: {getattr(settings, 'USE_X_FORWARDED_HOST', 'NOT SET')}<br>")
    
    return HttpResponse("".join(info))

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
    from django.utils import timezone
    
    # Obtener las últimas 5 noticias publicadas
    noticias_recientes = Noticia.objects.filter(
        publicada=True,
        fecha_publicacion__lte=timezone.now()
    ).order_by('-fecha_publicacion')[:5]
    
    # Obtener las próximas 5 actividades
    actividades_proximas = Actividad.objects.filter(
        fecha__gte=timezone.now().date()
    ).order_by('fecha', 'hora_comienzo')[:5]
    
    context = {
        'noticias_recientes': noticias_recientes,
        'actividades_proximas': actividades_proximas,
    }
    
    return render(request, 'usuarios/home.html', context)

@login_required
def dashboard(request):
    return render(request, 'usuarios/dashboard.html')

def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('home')
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
            'titulo': actividad.titulo or f"{actividad.get_tipo_actividad_display()}",
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
                'titulo': actividad.titulo or actividad.get_tipo_actividad_display(),
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
                'titulo': actividad.titulo or actividad.get_tipo_actividad_display(),
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
                    'titulo': actividad_actualizada.titulo or actividad_actualizada.get_tipo_actividad_display(),
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

def get_latest_menus():
    """Busca automáticamente los menús más recientes disponibles"""
    import os
    from datetime import datetime
    import re
    
    # Directorio donde están los menús
    media_root = getattr(settings, 'MEDIA_ROOT', '')
    comedor_dir = os.path.join(media_root, 'comedor')
    
    menus_disponibles = []
    mes_actual = None
    fecha_actualizacion = None
    
    if os.path.exists(comedor_dir):
        # Obtener todos los archivos PDF del directorio
        pdf_files = [f for f in os.listdir(comedor_dir) if f.endswith('.pdf')]
        
        # Diccionario para agrupar menús por mes e idioma
        menus_por_mes = {}
        
        for pdf_file in pdf_files:
            # Extraer información del nombre del archivo
            # Formatos esperados: menu_[mes]_castellano.pdf, menu_[mes]_euskera.pdf
            match = re.match(r'menu_(\w+)_(castellano|euskera)\.pdf', pdf_file, re.IGNORECASE)
            
            if match:
                mes, idioma = match.groups()
                
                # Normalizar el nombre del mes
                mes_normalized = mes.lower()
                idioma_normalized = idioma.lower()
                
                if mes_normalized not in menus_por_mes:
                    menus_por_mes[mes_normalized] = {}
                
                # Obtener fecha de modificación del archivo
                file_path = os.path.join(comedor_dir, pdf_file)
                file_mtime = os.path.getmtime(file_path)
                file_date = datetime.fromtimestamp(file_mtime)
                
                menus_por_mes[mes_normalized][idioma_normalized] = {
                    'archivo': pdf_file,
                    'fecha_mod': file_mtime,
                    'fecha_formateada': file_date.strftime('%d/%m/%Y %H:%M'),
                    'titulo': f"Menú {mes.title()} ({idioma.title()})"
                }
        
        # Encontrar el mes más reciente
        if menus_por_mes:
            # Ordenar por fecha de modificación más reciente
            mes_mas_reciente = None
            fecha_mas_reciente = 0
            
            for mes, idiomas in menus_por_mes.items():
                # Obtener la fecha más reciente de los archivos de este mes
                max_fecha = max(info['fecha_mod'] for info in idiomas.values())
                if max_fecha > fecha_mas_reciente:
                    fecha_mas_reciente = max_fecha
                    mes_mas_reciente = mes
            
            if mes_mas_reciente:
                mes_actual = mes_mas_reciente.title()
                fecha_actualizacion = datetime.fromtimestamp(fecha_mas_reciente)
                
                # Agregar menús del mes más reciente
                idiomas_info = menus_por_mes[mes_mas_reciente]
                
                # Orden preferido: castellano primero, luego euskera
                orden_idiomas = ['castellano', 'euskera']
                
                for idioma in orden_idiomas:
                    if idioma in idiomas_info:
                        info = idiomas_info[idioma]
                        menus_disponibles.append({
                            'titulo': info['titulo'],
                            'archivo': info['archivo'],
                            'idioma': idioma.title(),
                            'fecha_actualizacion': info['fecha_formateada']
                        })
    
    # Si no se encuentran menús, usar valores por defecto
    if not menus_disponibles:
        current_month = datetime.now().strftime('%B').lower()
        month_translations = {
            'january': 'enero', 'february': 'febrero', 'march': 'marzo',
            'april': 'abril', 'may': 'mayo', 'june': 'junio',
            'july': 'julio', 'august': 'agosto', 'september': 'septiembre',
            'october': 'octubre', 'november': 'noviembre', 'december': 'diciembre'
        }
        mes_actual = month_translations.get(current_month, 'Mes actual').title()
        
        menus_disponibles = [
            {
                'titulo': f'Menú {mes_actual} (No disponible)',
                'archivo': 'no_disponible.pdf',
                'idioma': 'No disponible',
                'fecha_actualizacion': 'N/A'
            }
        ]
    
    return mes_actual, menus_disponibles, fecha_actualizacion

def comedor(request):
    """Vista para mostrar información del comedor escolar"""
    
    # Obtener menús dinámicamente
    mes_actual, menus_disponibles, fecha_actualizacion = get_latest_menus()
    
    # Información del comedor
    menu_info = {
        'mes_actual': mes_actual,
        'fecha_actualizacion': fecha_actualizacion.strftime('%d/%m/%Y %H:%M') if fecha_actualizacion else None,
        'empresa': 'El Gusto de Crecer',
        'descripcion': 'Empresa especializada en catering escolar con más de 15 años de experiencia. Elaboramos menús equilibrados y adaptados a las necesidades nutricionales de los escolares.',
        'contacto_empresa': {
            'nombre': 'El Gusto de Crecer',
            'email': 'elgustodecrecer@aramark.es',
            'web': 'www.elgustodecrecer.es'
        },
        'menus_disponibles': menus_disponibles
    }
    
    return render(request, 'usuarios/comedor.html', {'menu_info': menu_info})

@login_required
def gestionar_menus(request):
    """Vista para gestionar menús del comedor (solo staff)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('comedor')
    
    media_dir = os.path.join(settings.MEDIA_ROOT, 'comedor')
    
    # Crear directorio si no existe
    os.makedirs(media_dir, exist_ok=True)
    
    if request.method == 'POST':
        if 'upload' in request.POST:
            # Manejar subida de archivos
            return handle_menu_upload(request, media_dir)
        elif 'delete' in request.POST:
            # Manejar eliminación de archivos
            return handle_menu_delete(request, media_dir)
    
    # Obtener lista de menús existentes
    pdf_files = []
    if os.path.exists(media_dir):
        files = [f for f in os.listdir(media_dir) if f.endswith('.pdf')]
        for file in sorted(files):
            file_path = os.path.join(media_dir, file)
            file_stat = os.stat(file_path)
            pdf_files.append({
                'nombre': file,
                'tamaño': file_stat.st_size,
                'fecha_mod': datetime.fromtimestamp(file_stat.st_mtime),
                'url': f'/comedor/pdf/{file}/'
            })
    
    context = {
        'menus_existentes': pdf_files,
        'total_archivos': len(pdf_files)
    }
    
    return render(request, 'usuarios/gestionar_menus.html', context)

def extraescolares(request):
    """Vista para mostrar información de las actividades extraescolares"""
    
    # Lista de extraescolares disponibles
    extraescolares_disponibles = [
        {
            'nombre': 'TEATRO',
            'icono': 'bi-mask',
            'detalles': {
                'impartida_por': 'María Araiz',
                'horario_dia': 'Jueves/Osteguna',
                'horario_hora': '16:30 - 17:30',
                'edad': 'A partir de 4ºE.P./LH 4 mailatik aurrera',
                'precio': '30€/mes'
            }
        },
        {
            'nombre': 'TALLER DE CREATIVIDAD', 
            'icono': 'bi-palette',
            'detalles': {
                'impartida_por': 'Alaitz López Lameiro',
                'horario_dia': 'Jueves/Osteguna',
                'horario_hora': 'Mediodía después de la comida',
                'edad': 'Todas las edades/Adin guztiak',
                'precio': '35€/mes + material inicial',
                'idiomas': 'Euskera - Castellano',
                'descripcion': 'Taller de creación artística donde los participantes pueden explorar diferentes técnicas y materiales para desarrollar su creatividad y habilidades artísticas.',
                'descripcion_eu': 'Arte sormen tailerra, parte-hartzaileek teknika eta material ezberdinak esploratu ditzaketen beren sormena eta arte trebetasunak garatzeko.'
            }
        },
        {
            'nombre': 'ROBÓTICA',
            'icono': 'bi-robot',
            'detalles': {
                'impartida_por': 'DiscoverBricks',
                'url': 'https://discoverbricks.es/',
                'horario_dia': 'Viernes/Ostirala',
                'horario_hora': '16:30 - 17:30',
                'edad': 'A partir de 1ºE.P. / LH 1 mailatik aurrera',
                'precio': '36€/mes'
            }
        },
        {
            'nombre': 'PATINAJE',
            'icono': 'bi-lightning',
            'detalles': {
                'impartida_por': 'Manu Goñi',
                'horario_dia': 'Miércoles/Asteazkena',
                'horario_hora': '15:00 - 16:30',
                'edad': 'A partir de 2º E.I. / HH 4 urtetik aurrera',
                'precio': '20€/mes'
            }
        },
        {
            'nombre': 'JUDO',
            'icono': 'bi-trophy',
            'detalles': {
                'impartida_por': 'Andrés López Moreno',
                'horario_dia': 'Lunes-Jueves / Astelehena - Osteguna',
                'horario_hora': '16:30 - 17:30',
                'edad': 'A partir de 3º E.I. / HH 5 Urtetik aurrera',
                'precio': '34€/mes'
            }
        },
        {
            'nombre': 'TALLER DE COSTURA',
            'icono': 'bi-scissors',
            'detalles': {
                'impartida_por': 'María Leorza',
                'horario_dia': 'Lunes o Martes/Astelehena edo Asteartea',
                'horario_hora': 'Mediodía después de la comida',
                'edad': 'A partir de 3º E.I./HH 5 urtetik aurrera',
                'precio': '30€/mes + material inicial'
            }
        }
    ]
    
    # Información general
    info_extraescolares = {
        'plazo_inicio': '25 de Agosto',
        'plazo_fin': '16 de Septiembre',
        'formulario_url': 'https://docs.google.com/forms/d/e/1FAIpQLScuN-0ExifKUNCfpzrv-vWdFYoG0NbepxXGRkstMfOFwWUgSw/viewform?usp=dialog',
        'extraescolares': extraescolares_disponibles
    }
    
    return render(request, 'usuarios/extraescolares.html', {'info': info_extraescolares})

def handle_menu_upload(request, media_dir):
    """Maneja la subida de archivos de menú"""
    try:
        uploaded_files = request.FILES.getlist('menu_files')
        
        if not uploaded_files:
            messages.error(request, 'No se seleccionaron archivos para subir.')
            return redirect('gestionar_menus')
        
        success_count = 0
        for uploaded_file in uploaded_files:
            # Validar que sea un PDF
            if not uploaded_file.name.endswith('.pdf'):
                messages.warning(request, f'Archivo {uploaded_file.name} no es un PDF y fue omitido.')
                continue
            
            # Validar tamaño (máximo 10MB)
            if uploaded_file.size > 10 * 1024 * 1024:
                messages.warning(request, f'Archivo {uploaded_file.name} es demasiado grande (máximo 10MB).')
                continue
            
            # Limpiar nombre del archivo
            safe_name = uploaded_file.name.replace(' ', '_').lower()
            file_path = os.path.join(media_dir, safe_name)
            
            # Guardar archivo
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            success_count += 1
            messages.success(request, f'Archivo {safe_name} subido correctamente.')
        
        if success_count > 0:
            messages.success(request, f'Se subieron {success_count} archivos exitosamente.')
        
    except Exception as e:
        messages.error(request, f'Error subiendo archivos: {e}')
    
    return redirect('gestionar_menus')

def handle_menu_delete(request, media_dir):
    """Maneja la eliminación de archivos de menú"""
    try:
        file_to_delete = request.POST.get('file_name')
        
        if not file_to_delete:
            messages.error(request, 'No se especificó archivo para eliminar.')
            return redirect('gestionar_menus')
        
        file_path = os.path.join(media_dir, file_to_delete)
        
        # Verificar que el archivo existe y está dentro del directorio permitido
        if not os.path.exists(file_path) or not os.path.commonpath([file_path, media_dir]) == media_dir:
            messages.error(request, 'Archivo no encontrado o acceso denegado.')
            return redirect('gestionar_menus')
        
        # Eliminar archivo
        os.remove(file_path)
        messages.success(request, f'Archivo {file_to_delete} eliminado correctamente.')
        
    except Exception as e:
        messages.error(request, f'Error eliminando archivo: {e}')
    
    return redirect('gestionar_menus')

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


def noticias_lista(request):
    """Vista para mostrar la lista de noticias"""
    from django.core.paginator import Paginator
    
    # Obtener solo noticias publicadas
    noticias = Noticia.objects.filter(publicada=True)
    
    # Obtener idioma actual
    language = request.LANGUAGE_CODE
    
    # Añadir campos localizados a cada noticia
    for noticia in noticias:
        noticia.titulo_localizado = noticia.get_titulo_localized(language)
        noticia.resumen_localizado = noticia.get_resumen_localized(language)
        noticia.contenido_localizado = noticia.get_contenido_localized(language)
    
    # Paginación
    paginator = Paginator(noticias, 6)  # 6 noticias por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # También añadir los campos localizados a las noticias paginadas
    for noticia in page_obj:
        noticia.titulo_localizado = noticia.get_titulo_localized(language)
        noticia.resumen_localizado = noticia.get_resumen_localized(language)
        noticia.contenido_localizado = noticia.get_contenido_localized(language)
    
    context = {
        'noticias': page_obj,  # Para compatibilidad con la plantilla
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'language': language,
        'total_noticias': noticias.count(),
    }
    
    return render(request, 'usuarios/noticias_lista.html', context)


# Vista de detalle no necesaria con el modal
# def noticia_detalle(request, slug):
#     """Vista para mostrar el detalle de una noticia en modal"""
#     from django.shortcuts import get_object_or_404
#     
#     # Obtener la noticia por slug, solo si está publicada
#     noticia = get_object_or_404(Noticia, slug=slug, publicada=True)
#     
#     # Obtener idioma actual
#     language = request.LANGUAGE_CODE
#     
#     # Añadir campos localizados a la noticia
#     noticia.titulo_localizado = noticia.get_titulo_localized(language)
#     noticia.resumen_localizado = noticia.get_resumen_localized(language)
#     noticia.contenido_localizado = noticia.get_contenido_localized(language)
#     
#     # Obtener noticias relacionadas (las 3 más recientes, excluyendo la actual)
#     noticias_relacionadas = Noticia.objects.filter(
#         publicada=True
#     ).exclude(id=noticia.id)[:3]
#     
#     # Añadir campos localizados a las noticias relacionadas
#     for noticia_rel in noticias_relacionadas:
#         noticia_rel.titulo_localizado = noticia_rel.get_titulo_localized(language)
#         noticia_rel.resumen_localizado = noticia_rel.get_resumen_localized(language)
#         noticia_rel.contenido_localizado = noticia_rel.get_contenido_localized(language)
#     
#     context = {
#         'noticia': noticia,
#         'language': language,
#         'noticias_relacionadas': noticias_relacionadas,
#     }
#     
#     return render(request, 'usuarios/noticia_detalle.html', context)


@require_POST
@login_required
def crear_noticia(request):
    """Vista para crear una nueva noticia vía AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permisos para crear noticias'}, status=403)
    
    form = NoticiaForm(request.POST, request.FILES)
    if form.is_valid():
        noticia = form.save()
        return JsonResponse({
            'success': True,
            'message': 'Noticia creada exitosamente',
            'noticia_id': noticia.id
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


@require_POST
@login_required
def editar_noticia(request, noticia_id):
    """Vista para editar una noticia existente vía AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permisos para editar noticias'}, status=403)
    
    try:
        noticia = Noticia.objects.get(id=noticia_id)
    except Noticia.DoesNotExist:
        return JsonResponse({'error': 'Noticia no encontrada'}, status=404)
    
    form = NoticiaForm(request.POST, request.FILES, instance=noticia)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'Noticia actualizada exitosamente'
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


@login_required
@require_POST
def eliminar_noticia(request, noticia_id):
    """Vista para eliminar una noticia vía AJAX"""
    
    # Diagnóstico detallado
    print(f"DEBUG - Usuario: {request.user}")
    print(f"DEBUG - Is authenticated: {request.user.is_authenticated}")
    print(f"DEBUG - Is staff: {request.user.is_staff}")
    print(f"DEBUG - Method: {request.method}")
    print(f"DEBUG - CSRF token present: {'csrftoken' in request.COOKIES}")
    print(f"DEBUG - POST data: {request.POST}")
    print(f"DEBUG - Headers: {dict(request.headers)}")
    
    if not request.user.is_staff:
        error_msg = f'No tienes permisos para eliminar noticias. Usuario: {request.user.username if request.user.is_authenticated else "Anónimo"}, Staff: {request.user.is_staff}'
        print(f"DEBUG - Error: {error_msg}")
        return JsonResponse({'error': error_msg}, status=403)
    
    try:
        noticia = Noticia.objects.get(id=noticia_id)
        titulo = noticia.titulo
        
        # Eliminar imagen asociada si existe
        if noticia.imagen:
            try:
                if os.path.exists(noticia.imagen.path):
                    os.remove(noticia.imagen.path)
            except Exception as e:
                # Log del error pero continuar con la eliminación
                print(f"Error eliminando imagen: {e}")
        
        noticia.delete()
        print(f"DEBUG - Noticia eliminada exitosamente: {titulo}")
        return JsonResponse({
            'success': True,
            'message': f'Noticia "{titulo}" eliminada exitosamente'
        })
    except Noticia.DoesNotExist:
        error_msg = 'Noticia no encontrada'
        print(f"DEBUG - Error: {error_msg}")
        return JsonResponse({'error': error_msg}, status=404)
    except Exception as e:
        error_msg = f'Error inesperado: {str(e)}'
        print(f"DEBUG - Error: {error_msg}")
        return JsonResponse({'error': error_msg}, status=500)


@login_required
def obtener_noticia(request, noticia_id):
    """Vista para obtener los datos de una noticia para edición vía AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    try:
        noticia = Noticia.objects.get(id=noticia_id)
        data = {
            'id': noticia.id,
            'titulo': noticia.titulo,
            'titulo_eu': noticia.titulo_eu or '',
            'resumen': noticia.resumen,
            'resumen_eu': noticia.resumen_eu or '',
            'contenido': noticia.contenido,
            'contenido_eu': noticia.contenido_eu or '',
            'publicada': noticia.publicada,
            'imagen_url': noticia.imagen.url if noticia.imagen else ''
        }
        return JsonResponse(data)
    except Noticia.DoesNotExist:
        return JsonResponse({'error': 'Noticia no encontrada'}, status=404)

def obtener_noticia_publica(request, noticia_id):
    """Vista pública para obtener los datos de una noticia para mostrar en modal"""
    try:
        from django.utils import timezone
        
        noticia = Noticia.objects.get(
            id=noticia_id,
            publicada=True,
            fecha_publicacion__lte=timezone.now()
        )
        
        # Obtener idioma actual
        from django.utils.translation import get_language
        idioma_actual = get_language()
        
        # Seleccionar título y contenido según idioma
        if idioma_actual == 'eu' and noticia.titulo_eu:
            titulo = noticia.titulo_eu
            resumen = noticia.resumen_eu or noticia.resumen
            contenido = noticia.contenido_eu or noticia.contenido
        else:
            titulo = noticia.titulo
            resumen = noticia.resumen
            contenido = noticia.contenido
        
        data = {
            'success': True,
            'noticia': {
                'id': noticia.id,
                'titulo': titulo,
                'resumen': resumen,
                'contenido': contenido,
                'fecha_publicacion': noticia.fecha_publicacion.strftime('%d %B %Y'),
                'imagen': noticia.imagen.url if noticia.imagen else None,
                'destacada': getattr(noticia, 'destacada', False)
            }
        }
        return JsonResponse(data)
    except Noticia.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Noticia no encontrada'}, status=404)


def get_existing_menus():
    """Obtiene la lista de menús existentes"""
    import re
    from datetime import datetime
    
    media_root = getattr(settings, 'MEDIA_ROOT', '')
    comedor_dir = os.path.join(media_root, 'comedor')
    
    if not os.path.exists(comedor_dir):
        return {}
    
    pdf_files = [f for f in os.listdir(comedor_dir) if f.endswith('.pdf')]
    menus_por_mes = {}
    
    for pdf_file in pdf_files:
        match = re.match(r'menu_(\w+)_(castellano|euskera)\.pdf', pdf_file, re.IGNORECASE)
        
        if match:
            mes, idioma = match.groups()
            
            if mes not in menus_por_mes:
                menus_por_mes[mes] = {
                    'castellano': None,
                    'euskera': None,
                    'fecha_modificacion': None
                }
            
            file_path = os.path.join(comedor_dir, pdf_file)
            file_mtime = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(file_mtime)
            file_size = os.path.getsize(file_path)
            
            menus_por_mes[mes][idioma.lower()] = {
                'archivo': pdf_file,
                'fecha': file_date.strftime('%d/%m/%Y %H:%M'),
                'tamaño': f'{file_size:,} bytes'
            }
            
            # Actualizar fecha de modificación del mes (la más reciente)
            if (menus_por_mes[mes]['fecha_modificacion'] is None or 
                file_mtime > menus_por_mes[mes]['fecha_modificacion']):
                menus_por_mes[mes]['fecha_modificacion'] = file_mtime
    
    # Ordenar por fecha de modificación (más recientes primero)
    return dict(sorted(
        menus_por_mes.items(), 
        key=lambda x: x[1]['fecha_modificacion'] or 0, 
        reverse=True
    ))


def process_menu_upload(form_data):
    """Procesa la subida de menús"""
    mes = form_data['mes']
    menu_castellano = form_data.get('menu_castellano')
    menu_euskera = form_data.get('menu_euskera')
    menu_completo = form_data.get('menu_completo')
    sobrescribir = form_data.get('sobrescribir', False)
    
    media_root = getattr(settings, 'MEDIA_ROOT', '')
    comedor_dir = os.path.join(media_root, 'comedor')
    
    # Crear directorio si no existe
    os.makedirs(comedor_dir, exist_ok=True)
    
    archivos_procesados = []
    
    try:
        # Caso 1: Menú completo (separar páginas)
        if menu_completo:
            temp_path = os.path.join(comedor_dir, f'temp_{mes}_completo.pdf')
            
            # Guardar archivo temporal
            with open(temp_path, 'wb') as f:
                for chunk in menu_completo.chunks():
                    f.write(chunk)
            
            # Separar páginas
            success = split_menu_pdf_upload(temp_path, mes, sobrescribir)
            
            # Eliminar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if success:
                archivos_procesados.extend([f'menu_{mes}_castellano.pdf', f'menu_{mes}_euskera.pdf'])
            else:
                return {'success': False, 'message': 'Error separando el PDF completo'}
        
        # Caso 2: Archivos separados
        else:
            if menu_castellano:
                archivo_path = os.path.join(comedor_dir, f'menu_{mes}_castellano.pdf')
                
                if os.path.exists(archivo_path) and not sobrescribir:
                    return {'success': False, 'message': f'El menú de {mes} en castellano ya existe. Marca "sobrescribir" si quieres reemplazarlo.'}
                
                with open(archivo_path, 'wb') as f:
                    for chunk in menu_castellano.chunks():
                        f.write(chunk)
                
                archivos_procesados.append(f'menu_{mes}_castellano.pdf')
            
            if menu_euskera:
                archivo_path = os.path.join(comedor_dir, f'menu_{mes}_euskera.pdf')
                
                if os.path.exists(archivo_path) and not sobrescribir:
                    return {'success': False, 'message': f'El menú de {mes} en euskera ya existe. Marca "sobrescribir" si quieres reemplazarlo.'}
                
                with open(archivo_path, 'wb') as f:
                    for chunk in menu_euskera.chunks():
                        f.write(chunk)
                
                archivos_procesados.append(f'menu_{mes}_euskera.pdf')
        
        if archivos_procesados:
            return {
                'success': True, 
                'message': f'Menús subidos correctamente: {", ".join(archivos_procesados)}'
            }
        else:
            return {'success': False, 'message': 'No se procesó ningún archivo'}
    
    except Exception as e:
        return {'success': False, 'message': f'Error procesando archivos: {str(e)}'}


def split_menu_pdf_upload(pdf_path, mes, sobrescribir=False):
    """Separa un PDF de menú en castellano y euskera para uploads"""
    try:
        from pypdf import PdfReader, PdfWriter
        
        # Leer el PDF
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        if total_pages < 2:
            return False
        
        comedor_dir = os.path.dirname(pdf_path)
        
        # Crear PDF para castellano (primera página)
        castellano_path = os.path.join(comedor_dir, f'menu_{mes}_castellano.pdf')
        
        if os.path.exists(castellano_path) and not sobrescribir:
            return False
        
        writer_castellano = PdfWriter()
        writer_castellano.add_page(reader.pages[0])
        
        with open(castellano_path, 'wb') as output_file:
            writer_castellano.write(output_file)
        
        # Crear PDF para euskera (segunda página)
        euskera_path = os.path.join(comedor_dir, f'menu_{mes}_euskera.pdf')
        
        if os.path.exists(euskera_path) and not sobrescribir:
            # Si castellano se creó pero euskera no por sobrescribir, eliminar castellano
            if os.path.exists(castellano_path):
                os.remove(castellano_path)
            return False
        
        writer_euskera = PdfWriter()
        writer_euskera.add_page(reader.pages[1])
        
        with open(euskera_path, 'wb') as output_file:
            writer_euskera.write(output_file)
        
        return True
        
    except Exception as e:
        return False
