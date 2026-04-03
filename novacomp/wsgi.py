#!/usr/bin/env python3
"""
Ponto de entrada WSGI para Vercel - Força detecção como aplicação Flask
Este arquivo é automaticamente detectado pelo Vercel como entry point
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importa a aplicação Flask do dashboard
from web.dashboard import app as application

# Também expõe como 'app' para compatibilidade
app = application

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)
