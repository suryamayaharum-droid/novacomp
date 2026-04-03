# 🚀 Guia de Otimização para Vercel

## Melhorias Implementadas

### 1. **Builds Paralelos e Mais Rápidos**
- Configuração otimizada no `vercel.json` para instalação paralela de dependências
- Script `vercel_build.sh` para limpeza e otimização do build
- Uso de cache do pip desativado para builds mais limpos
- Remoção automática de arquivos desnecessários (.db, .pyc, __pycache__)

### 2. **Máquina de Build Otimizada**
- Runtime Python 3.9 configurado explicitamente
- Memória aumentada para 1024MB nas funções serverless
- Timeout estendido para 60 segundos para operações mais longas
- Limite de tamanho da Lambda: 50MB

### 3. **Sincronização Front-end/Back-end**
- Rotas separadas para API (`/api/*`) e front-end (`/*`)
- Variáveis de ambiente configuradas para garantir consistência
- Versões do cliente e servidor sincronizadas automaticamente

### 4. **Prevenção de Incompatibilidades**
- Arquivo `.vercelignore` para excluir arquivos desnecessários do deploy
- Dependências essenciais claramente definidas no `requirements.txt`
- Build script que remove conflitos potenciais

## Como Usar

### Deploy Automático (Recomendado)
```bash
# Conecte seu repositório Git ao Vercel
# Cada push para main fará deploy automático
git add .
git commit -m "Deploy otimizado"
git push origin main
```

### Deploy Manual com CLI
```bash
# Instalar Vercel CLI
npm install -g vercel

# Fazer deploy
cd novacomp
vercel --prod
```

### Variáveis de Ambiente Sugeridas
No painel do Vercel, configure:
- `PYTHON_VERSION=3.9`
- `PIP_INSTALL_PARALLEL=true`
- `BUILD_OPTIMIZATION=enabled`

## Estrutura de Rotas

| Rota | Destino | Descrição |
|------|---------|-----------|
| `/` | `api/index.py` | Dashboard principal |
| `/api/status` | `api/index.py` | Status da API |
| `/socket.io/*` | `api/index.py` | WebSocket em tempo real |

## Monitoramento

Após o deploy:
1. Acesse o dashboard em `https://seu-projeto.vercel.app`
2. Verifique logs em tempo real no painel do Vercel
3. Monitore performance nas métricas de função

## Troubleshooting

### Build lento
- Verifique se `PIP_NO_CACHE_DIR=1` está configurado
- Remova dependências não utilizadas do requirements.txt

### Erro de timeout
- Aumente `maxDuration` no vercel.json (máx: 60s para Hobby, 900s para Pro)
- Otimize queries e operações pesadas

### Incompatibilidade de versões
- Execute `vercel_build.sh` localmente para testar
- Verifique se todas as dependências são compatíveis com Python 3.9

## Próximos Passos

1. **Edge Functions**: Migrar rotas leves para Edge Functions para menor latência
2. **ISR**: Implementar Static Site Generation para páginas estáticas
3. **Monitoring**: Integrar com Vercel Analytics e Log Drain
