#!/bin/bash

echo "▶ Ejecutando tests de seguridad personalizados por app..."

# Lista de apps a testear
apps=("auth_user" "core" "custom_user" "order" "product" "shoppingCart")

# Iterar sobre cada app
for app in "${apps[@]}"
do
    echo "🔍 Testeando $app..."

    # Crear carpeta específica para la app dentro de security-tests
    APP_LOG_DIR="security-tests/$app"
    mkdir -p "$APP_LOG_DIR"

    # Definir archivo de log dentro de la carpeta de la app
    LOG_FILE="$APP_LOG_DIR/${app}_tests.log"

    # Ejecutar tests y guardar salida en logs
    python manage.py test "$app.tests.test_security" > "$LOG_FILE" 2>&1
done

echo "✅ Todos los tests han sido ejecutados. Revisa los logs en las carpetas correspondientes dentro de security-tests/"