# 🚨 INCIDENTE DE SEGURIDAD - CREDENCIALES EXPUESTAS

**Fecha de detección:** 14 de noviembre de 2025  
**Severidad:** CRÍTICA  
**Estado:** EN REMEDIACIÓN

## Descripción del Incidente

Se detectó que las credenciales de email de la cuenta `apymaremontivaladm@gmail.com` fueron expuestas en el código fuente del repositorio.

### Credenciales Comprometidas

- **Email:** apymaremontivaladm@gmail.com
- **App Password:** sqwx lhjv amix nxoz (COMPROMETIDA)
- **Archivo:** apyma_site/settings.py (líneas 160-161)
- **Repositorio:** robeche/apyma-remontival (GitHub)

## Acciones Inmediatas Requeridas

### ✅ COMPLETADO
- [x] Eliminar credenciales del código fuente
- [x] Implementar configuración con variables de entorno (.env)
- [x] Actualizar .gitignore para prevenir futuras exposiciones

### ⚠️ PENDIENTE - CRÍTICO
- [ ] **URGENTE:** Revocar App Password comprometida en Google
  - URL: https://myaccount.google.com/apppasswords
  - Eliminar contraseña: `sqwx lhjv amix nxoz`

- [ ] **URGENTE:** Cambiar contraseña de la cuenta Gmail
  - Cuenta: apymaremontivaladm@gmail.com
  - URL: https://myaccount.google.com/security

- [ ] Generar nueva App Password de Gmail
  - Usar nombre descriptivo: "Django Apyma Remontival"
  - Guardar en archivo .env (NO en código)

- [ ] Revisar actividad sospechosa en la cuenta
  - Correos enviados: https://mail.google.com/mail/u/0/#sent
  - Actividad reciente: https://myaccount.google.com/notifications
  - Dispositivos conectados: https://myaccount.google.com/device-activity

- [ ] Habilitar autenticación de dos factores (2FA)
  - URL: https://myaccount.google.com/signinoptions/two-step-verification

### 🔧 PENDIENTE - Post-Remediación
- [ ] Limpiar historial de Git (si el repo es público)
  - Usar BFG Repo-Cleaner o git filter-branch
  - Considerar crear nuevo repositorio

- [ ] Actualizar credenciales en PythonAnywhere (producción)
  - Variables de entorno en panel de configuración
  - Archivo .env en servidor

- [ ] Documentar procedimiento de manejo de secretos
  - Guía para el equipo

## Procedimiento para Configurar Nuevas Credenciales

### 1. Generar Nueva App Password de Gmail

```bash
# 1. Ir a Google Account
https://myaccount.google.com/apppasswords

# 2. Seleccionar "Correo" y "Otro (nombre personalizado)"
# 3. Nombrar: "Django Apyma Remontival"
# 4. Copiar la contraseña generada (16 caracteres con espacios)
```

### 2. Actualizar archivo .env

```bash
# Editar el archivo .env en la raíz del proyecto
EMAIL_HOST_USER=apymaremontivaladm@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # Nueva contraseña
```

### 3. Verificar que .env no se suba a Git

```bash
# Confirmar que .env está en .gitignore
git status
# No debe aparecer .env en la lista de cambios
```

### 4. Actualizar producción (PythonAnywhere)

- Dashboard → Files → Edit .env
- O usar variables de entorno del panel web

## Prevención Futura

### Checklist de Seguridad

- [ ] Nunca incluir credenciales en el código
- [ ] Usar variables de entorno para secretos
- [ ] Revisar código antes de commits
- [ ] Usar pre-commit hooks para detectar secretos
- [ ] Rotación periódica de credenciales (cada 3 meses)
- [ ] Revisar logs de acceso regularmente

### Herramientas Recomendadas

- **git-secrets:** Previene commits de credenciales
- **detect-secrets:** Escanea repositorio en busca de secretos
- **pre-commit:** Framework de hooks para Git

## Contacto

Para reportar incidentes de seguridad adicionales, contactar al administrador del sistema.

---
**Última actualización:** 14 de noviembre de 2025
