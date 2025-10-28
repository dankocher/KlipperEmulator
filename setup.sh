#!/usr/bin/env bash
set -euo pipefail

# Crear venv e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Crear carpetas de datos
mkdir -p data/uploads
mkdir -p data/thumbs

echo "✅ Entorno listo. Coloca tu printer.cfg en la raíz del proyecto."
