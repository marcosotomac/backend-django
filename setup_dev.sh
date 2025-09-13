#!/bin/bash

# Script de configuración rápida para desarrollo

echo "🚀 Configurando Social Network Backend..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    print_error "No se encontró manage.py. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

print_status "Verificando entorno virtual..."

# Verificar si el entorno virtual está activado
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "Entorno virtual activo: $VIRTUAL_ENV"
else
    print_warning "Entorno virtual no detectado. Asegúrate de activarlo con: source venv/bin/activate"
fi

print_status "Instalando dependencias..."
pip install -r requirements.txt

print_status "Creando directorios de media..."
mkdir -p media/avatars media/posts media/uploads

print_status "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

print_status "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

print_status "Verificando configuración..."
python manage.py check

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Crear superusuario: python manage.py createsuperuser"
echo "2. Ejecutar servidor: python manage.py runserver"
echo "3. Visitar: http://127.0.0.1:8000/"
echo "4. Admin: http://127.0.0.1:8000/admin/"
echo "5. Swagger: http://127.0.0.1:8000/swagger/"
echo ""
echo "🛠️ Comandos útiles:"
echo "   - Crear superusuario: python manage.py createsuperuser"
echo "   - Ejecutar tests: python manage.py test"
echo "   - Shell Django: python manage.py shell"
echo ""