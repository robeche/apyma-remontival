# Apyma Remontival - Aplicación Web

Aplicación web oficial de la Asociación de Padres y Madres de Alumnos del CP Remontival IP.

## 🚀 Características

- ✅ **Formulario de contacto** con envío por email
- ✅ **Carousel de imágenes** en la página principal
- ✅ **Soporte bilingüe** (Castellano/Euskera)
- ✅ **Sistema de usuarios** y área de socios
- ✅ **Diseño responsive** con Bootstrap 5
- ✅ **Panel de administración** Django

## 🛠️ Desarrollo

### Requisitos
- Python 3.12+
- Django 5.2+
- SQLite (desarrollo) / PostgreSQL (producción)

### Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd ApymaRemontival
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install django pillow
```

4. **Aplicar migraciones**
```bash
python manage.py migrate
```

5. **Crear superusuario**
```bash
python manage.py createsuperuser
```

6. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

### Configuración de Entornos

El proyecto usa configuraciones separadas:

- **Desarrollo**: `apyma_site.settings.development`
- **Producción**: `apyma_site.settings.production`

#### Variables de entorno para producción

Copia `.env.example` a `.env` y configura:

```bash
SECRET_KEY=tu_clave_secreta
EMAIL_HOST_USER=apymaremontivaladm@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_aplicacion
DB_NAME=apyma_db
DB_USER=apyma_user
DB_PASSWORD=password_seguro
```

## 🌐 Despliegue

### PythonAnywhere (Recomendado)

1. Sube el código a PythonAnywhere
2. Configura la aplicación web con `apyma_site.settings.production`
3. Configura las variables de entorno
4. Ejecuta `python manage.py collectstatic`
5. Ejecuta `python manage.py migrate`

### Otros hostings

El proyecto está configurado para:
- Heroku
- DigitalOcean
- VPS con Nginx/Apache

## 📧 Configuración de Email

Para que funcione el envío de emails:

1. Configura una cuenta Gmail con autenticación en 2 pasos
2. Genera una contraseña de aplicación
3. Actualiza las variables de entorno

## 🗂️ Estructura del Proyecto

```
ApymaRemontival/
├── apyma_site/
│   ├── settings/
│   │   ├── base.py           # Configuración común
│   │   ├── development.py    # Desarrollo
│   │   └── production.py     # Producción
│   ├── urls.py
│   └── wsgi.py
├── usuarios/
│   ├── models.py            # Modelo Contacto
│   ├── views.py             # Vistas (contacto, home, etc.)
│   ├── forms.py             # Formulario de contacto
│   └── templates/           # Plantillas HTML
├── media/                   # Imágenes del carousel
├── locale/                  # Traducciones euskera
└── manage.py
```

## 🤝 Contribuir

1. Fork del proyecto
2. Crea una rama para tu feature
3. Commit de cambios
4. Push a la rama
5. Abre un Pull Request

## 📝 Licencia

Proyecto de la Apyma Remontival - CP Remontival IP