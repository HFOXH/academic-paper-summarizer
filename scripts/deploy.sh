#!/bin/bash

set -e  # si algo falla, se detiene todo

echo "======================================"
echo "🚀 Iniciando deploy con Terraform"
echo "======================================"

# Ir a la carpeta de terraform (ajusta si tu estructura cambia)
cd "$(dirname "$0")/.."

echo "📦 Inicializando Terraform..."
terraform init

echo "🔍 Validando configuración..."
terraform validate

echo "📊 Generando plan..."
terraform plan -out=tfplan

echo "⚡ Aplicando infraestructura..."
terraform apply tfplan

echo "🧹 Limpiando archivos temporales..."
rm -f tfplan

echo "======================================"
echo "✅ Deploy completado exitosamente"
echo "======================================"