# Instrucciones de Despliegue en PythonAnywhere

## Guía paso a paso para desplegar Apyma Remontival

### 1. Crear cuenta en PythonAnywhere
- Ve a: https://www.pythonanywhere.com/
- Crear cuenta gratuita (Beginner account)
- Username sugerido: `apymaremontival` o similar

### 2. Subir código
En el dashboard de PythonAnywhere, ve a "Files" y sube el proyecto o clona desde Git.

**Opción A: Upload directo**
- Comprimir carpeta del proyecto en .zip
- Subir desde la pestaña "Files"
- Extraer en `/home/yourusername/`

**Opción B: Git clone (recomendado)**
```bash
# En la consola de PythonAnywhere
cd ~
git clone https://github.com/tuusuario/ApymaRemontival.git
cd ApymaRemontival
```

### 3. Instalar dependencias
```bash
# En la consola de PythonAnywhere
cd ~/ApymaRemontival
pip3.10 install --user -r requirements.txt
```

### 4. Configurar aplicación web
- Ve a la pestaña "Web"
- "Add a new web app"
- Seleccionar "Manual configuration"
- Python 3.10
- Directorio: `/home/yourusername/ApymaRemontival`

### 5. Configurar WSGI
Editar el archivo WSGI en `/var/www/yourusername_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

# Añadir el directorio del proyecto
path = '/home/yourusername/ApymaRemontival'
if path not in sys.path:
    sys.path.append(path)

# Configurar variables de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apyma_site.settings.production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 6. Configurar variables de entorno
Crear archivo `.env` en `/home/yourusername/ApymaRemontival/.env`:

```bash
SECRET_KEY=tu_clave_secreta_super_larga_y_segura_aqui
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
EMAIL_HOST_USER=apymaremontivaladm@gmail.com
EMAIL_HOST_PASSWORD=sqwx lhjv amix nxoz
```

### 7. Configurar archivos estáticos
```bash
cd ~/ApymaRemontival
python3.10 manage.py collectstatic --noinput
```

En la pestaña "Web" de PythonAnywhere:
- Static files URL: `/static/`
- Static files directory: `/home/yourusername/ApymaRemontival/staticfiles/`

### 8. Configurar archivos media
En la pestaña "Web":
- Static files URL: `/media/`
- Static files directory: `/home/yourusername/ApymaRemontival/media/`

### 9. Ejecutar migraciones
```bash
cd ~/ApymaRemontival
python3.10 manage.py migrate
```

### 10. Crear superusuario
```bash
python3.10 manage.py createsuperuser
```

### 11. Recargar aplicación
- En la pestaña "Web", hacer clic en "Reload yourusername.pythonanywhere.com"

### 12. Probar
- Visitar: https://yourusername.pythonanywhere.com
- Probar formulario de contacto
- Verificar que se reciben emails

## Notas importantes:
- La cuenta gratuita tiene limitaciones de CPU
- Los archivos se mantienen por 3 meses de inactividad
- Para dominio personalizado necesitas cuenta de pago
- Los emails funcionan sin restricciones

## Solución de problemas:
- Logs en "Tasks" > "Error logs"
- Consola para debug: "Consoles" > "Bash"
- Recargar app después de cambios