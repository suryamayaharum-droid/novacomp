#!/bin/bash
# Script de build otimizado para Vercel

echo "🚀 Otimizando build do NovaComp..."

# Instalar dependências em paralelo
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar apenas dependências essenciais para produção
pip install -r requirements.txt --no-cache-dir

# Remover arquivos desnecessários
find . -type f -name "*.db" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

echo "✅ Build otimizado concluído!"
