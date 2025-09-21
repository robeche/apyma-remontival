from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .forms import ContactoForm
from .models import Contacto

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
