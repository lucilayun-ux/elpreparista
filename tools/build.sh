#!/usr/bin/env bash
# Regenera todo lo que sale de index.html. Ejecutar desde la carpeta del repositorio
# después de cualquier cambio en index.html:
#   1. Deja escrito en index.html el contenido de la lista (para buscadores e IA).
#   2. Genera la versión inglesa en.html.
#   3. Deja escrito también el contenido de en.html.
set -euo pipefail
cd "$(dirname "$0")/.."
export NODE_PATH="${NODE_PATH:-$(npm root -g)}"
node tools/prerender.js
python3 tools/build_en.py
node tools/prerender.js
