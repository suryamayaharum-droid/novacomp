#!/bin/bash
# Script de build corrigido para evitar erro 127 (comando não encontrado)

echo "=== Iniciando Build Otimizado ==="

# Instalar dependências Python explicitamente
echo "Instalando dependências..."
pip install -r requirements.txt --no-cache-dir

# Verificar se a instalação foi bem sucedida
if [ $? -ne 0 ]; then
    echo "Erro na instalação das dependências"
    exit 1
fi

echo "Dependências instaladas com sucesso"

# Não executar build command para aplicações Flask puras
# O Vercel detectará automaticamente o ponto de entrada
echo "Build concluído - aplicação Flask pronta para deploy"
exit 0
