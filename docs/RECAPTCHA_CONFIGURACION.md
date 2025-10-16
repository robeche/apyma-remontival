# 🔐 Configuración de reCAPTCHA por Entornos

## 🛠️ **Desarrollo (Local)**

### **Configuración actual:**
- ✅ **Archivo**: `apyma_site/settings/development.py`
- ✅ **Claves**: De prueba de Google (funcionan automáticamente)
- ✅ **Mensaje**: "This reCAPTCHA is for testing purposes only" (normal)

```python
# En development.py
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'  # Test key
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'  # Test key
```

---

## 🚀 **Producción (PythonAnywhere)**

### **1. Crear claves reales de reCAPTCHA:**
1. Ve a: https://www.google.com/recaptcha/admin/create
2. **Tipo**: reCAPTCHA v2 "I'm not a robot" Checkbox
3. **Dominios**: Añade tu dominio (ej: `robeche.pythonanywhere.com`)
4. **Obtén las claves**: Site Key (pública) y Secret Key (privada)

### **2. Configurar variables de entorno en PythonAnywhere:**

#### **Opción A: Archivo .env (Recomendado)**
```bash
# En PythonAnywhere Console
cd /home/tuusuario
nano .env
```

```bash
# Contenido del archivo .env
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=False
RECAPTCHA_PUBLIC_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_PRIVATE_KEY=6LcYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
```

#### **Opción B: Variables de entorno del sistema**
```bash
# En PythonAnywhere Console
echo 'export RECAPTCHA_PUBLIC_KEY="tu-site-key"' >> ~/.bashrc
echo 'export RECAPTCHA_PRIVATE_KEY="tu-secret-key"' >> ~/.bashrc
source ~/.bashrc
```

### **3. Verificar configuración:**
```bash
# En PythonAnywhere Console
cd /home/tuusuario/mysite
python manage.py shell

# En shell de Django
from django.conf import settings
print("Public Key:", settings.RECAPTCHA_PUBLIC_KEY)
print("Private Key:", settings.RECAPTCHA_PRIVATE_KEY[:10] + "...")
```

---

## 📋 **Configuración Completada**

### **✅ Desarrollo:**
- **Claves**: Automáticas de Google (test)
- **Mensaje**: "This reCAPTCHA is for testing purposes only"
- **Funciona**: ✅ Sin configuración adicional

### **🔧 Producción (Pendiente):**
- **Claves**: Variables de entorno desde .env o sistema
- **Mensaje**: Desaparece automáticamente con claves reales
- **Configurar**: Crear cuenta en Google reCAPTCHA

---

## 🎯 **Siguiente Paso**

**Para ir a producción**, solo necesitas:
1. **Registrarte** en Google reCAPTCHA (5 minutos)
2. **Configurar** las variables de entorno en PythonAnywhere
3. **¡Listo!** El captcha funcionará sin el mensaje de prueba

### **Estado actual**: ✅ Funcionando en desarrollo con claves de prueba