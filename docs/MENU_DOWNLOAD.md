# Descarga Automática de Menús del Comedor

Este sistema permite descargar automáticamente los menús del comedor desde el área personal de El Gusto de Crecer.

## 🚀 Configuración Inicial

### 1. Instalar dependencias
```bash
pip install beautifulsoup4 lxml requests
```

### 2. Configurar credenciales
```bash
# Opción 1: Usando el script de configuración
python scripts/setup_menu_download.py --setup

# Opción 2: Usando comando Django
python manage.py download_menus --setup
```

Te pedirá:
- 📧 Tu email de acceso al área personal
- 🔑 Tu contraseña

Las credenciales se guardan de forma segura en `.menu_credentials.json`

## 📥 Descargar Menús

### Manualmente
```bash
# Opción 1: Script directo
python scripts/download_menus_automated.py

# Opción 2: Comando Django
python manage.py download_menus

# Opción 3: Con credenciales específicas
python scripts/download_menus_automated.py --email tu@email.com --password tupassword
```

### Usando archivo batch (Windows)
```bash
# Crear archivo batch
python scripts/setup_menu_download.py --create-batch

# Después hacer doble clic en descargar_menus.bat
```

## 🔄 Automatización Mensual

### Windows - Programador de Tareas

1. Abrir "Programador de tareas" (`taskschd.msc`)
2. Crear tarea básica
3. Configurar:
   - **Nombre**: Descarga Menús Comedor
   - **Desencadenador**: Mensualmente (día 1 de cada mes)
   - **Acción**: Iniciar programa
   - **Programa**: `X:\Proyectos\ApymaRemontival\.venv\Scripts\python.exe`
   - **Argumentos**: `X:\Proyectos\ApymaRemontival\scripts\download_menus_automated.py`
   - **Directorio**: `X:\Proyectos\ApymaRemontival`

### Linux/Mac - Cron Job
```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar el primer día de cada mes a las 8:00 AM
0 8 1 * * cd /ruta/al/proyecto && python scripts/download_menus_automated.py
```

## 📋 Verificar Estado

```bash
# Ver archivos descargados y configuración
python scripts/setup_menu_download.py --status

# O usando Django
python manage.py download_menus --status
```

## 📁 Archivos Descargados

Los menús se guardan en:
```
media/comedor/menu_[descripcion]_[YYYYMM].pdf
```

Ejemplos:
- `menu_BASAL_OCTUBRE_202510.pdf`
- `menu_Menu_Escolar_Octubre_202510.pdf`

## 🔧 Resolución de Problemas

### Error de credenciales
```bash
# Reconfigurar credenciales
python scripts/setup_menu_download.py --setup
```

### No se encuentran menús
1. Verifica que tus credenciales sean correctas
2. Revisa que el sitio web esté disponible
3. El script busca enlaces a PDFs con palabras clave: menu, menú, comedor, basal, alimentación

### Error de conexión
- Verifica tu conexión a internet
- El sitio web puede estar temporalmente no disponible

## 🔐 Seguridad

- Las credenciales se almacenan localmente en `.menu_credentials.json`
- El archivo tiene permisos restringidos (solo lectura para el usuario)
- **No subas este archivo al repositorio** (está en .gitignore)

## 📝 Logs y Monitoreo

El script muestra información detallada durante la ejecución:
- ✅ Operaciones exitosas
- ⚠️ Advertencias
- ❌ Errores
- 📥 Descargas en progreso
- 📋 Menús encontrados

## 🛠️ Desarrollo

### Estructura de archivos
```
scripts/
├── download_menus_automated.py      # Script principal
├── setup_menu_download.py          # Configuración y pruebas
├── download_menus.py               # Script anterior (URLs directas)
└── download_menus_simple.py        # Versión simple

usuarios/management/commands/
└── download_menus.py               # Comando Django
```

### Modificar el comportamiento

Para cambiar la lógica de búsqueda de menús, edita la función `find_menu_links()` en `download_menus_automated.py`:

```python
# Buscar palabras clave diferentes
menu_keywords = ['menu', 'menú', 'comedor', 'basal', 'alimentación']

# Cambiar URLs de búsqueda
possible_urls = [
    f"{self.base_url}/AreaPersonal",
    f"{self.base_url}/menus",
    # Agregar más URLs aquí
]
```

## 📞 Soporte

Si tienes problemas:
1. Verifica la configuración con `--status`
2. Prueba el login manualmente en la web
3. Revisa los logs de error del script
4. Contacta al administrador del sistema