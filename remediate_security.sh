#!/bin/bash
# Script de ayuda para remediar la exposición de credenciales
# APYMA REMONTIVAL - Incidente de Seguridad

echo "=============================================="
echo "REMEDIACIÓN DE CREDENCIALES EXPUESTAS"
echo "APYMA REMONTIVAL"
echo "=============================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}⚠️  ACCIONES CRÍTICAS PENDIENTES${NC}"
echo ""
echo "1. REVOCAR App Password comprometida de Gmail"
echo "   - Ir a: https://myaccount.google.com/apppasswords"
echo "   - Buscar y eliminar contraseña: sqwx lhjv amix nxoz"
echo ""

echo "2. CAMBIAR contraseña de la cuenta Gmail"
echo "   - Ir a: https://myaccount.google.com/security"
echo "   - Cambiar contraseña de: apymaremontivaladm@gmail.com"
echo ""

echo "3. GENERAR nueva App Password"
echo "   - Ir a: https://myaccount.google.com/apppasswords"
echo "   - Crear nueva con nombre: 'Django Apyma Remontival'"
echo "   - Copiar la contraseña generada (16 caracteres)"
echo ""

echo "4. ACTUALIZAR archivo .env con nueva contraseña"
echo "   - Editar: .env"
echo "   - Cambiar EMAIL_HOST_PASSWORD=NUEVA_CONTRASEÑA"
echo ""

echo -e "${YELLOW}📋 VERIFICACIONES DE SEGURIDAD${NC}"
echo ""
echo "5. REVISAR actividad sospechosa en Gmail"
echo "   - Correos enviados: https://mail.google.com/mail/u/0/#sent"
echo "   - Actividad: https://myaccount.google.com/notifications"
echo ""

echo "6. HABILITAR autenticación de dos factores (2FA)"
echo "   - Ir a: https://myaccount.google.com/signinoptions/two-step-verification"
echo ""

echo -e "${GREEN}✅ CAMBIOS EN CÓDIGO (COMPLETADOS)${NC}"
echo "   - Credenciales eliminadas del código fuente"
echo "   - Configuración movida a variables de entorno"
echo "   - .gitignore actualizado"
echo "   - Archivo .env creado"
echo ""

echo -e "${YELLOW}🔧 PRÓXIMOS PASOS${NC}"
echo ""
echo "A. Commit de cambios de seguridad:"
echo "   git add .gitignore apyma_site/settings.py .env.example"
echo "   git commit -m 'security: remove exposed credentials, use environment variables'"
echo "   git push"
echo ""

echo "B. Limpiar historial de Git (OPCIONAL pero RECOMENDADO):"
echo "   - Usar BFG Repo-Cleaner para eliminar credenciales del historial"
echo "   - Documentación: https://rtyley.github.io/bfg-repo-cleaner/"
echo ""

echo "C. Actualizar producción (PythonAnywhere):"
echo "   - Subir archivo .env con nuevas credenciales"
echo "   - O configurar variables de entorno en el panel web"
echo ""

echo -e "${RED}⚠️  IMPORTANTE: Ejecuta los pasos 1-4 INMEDIATAMENTE${NC}"
echo ""
