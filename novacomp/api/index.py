#!/usr/bin/env python3
"""
Ponto de entrada para Vercel - Adapta o NovaComp para rodar na plataforma
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importa a aplicação Flask do dashboard
from web.dashboard import app as flask_app

# Expõe a aplicação para o Vercel
app = flask_app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
