# NovaComp — Estado de progresso

Atualizado em 2026-10-20.

## Objetivo
Construir a base persistente da agente Nova: continuidade de tarefas, checkpoints recuperáveis, fila durável, registro de evidências e propostas de melhoria limitadas.

## Verificado
- API FastAPI publicada na Vercel; a última implantação previamente consultada estava `READY`.
- `/api/health` respondeu HTTP 200 no checkpoint anterior.
- `/openapi.json` listou as rotas da API, incluindo fila, checkpoints e propostas de evolução.
- Banco Neon configurado; tabela `novacomp_task_queue` e permissões básicas da role de aplicação foram verificadas anteriormente.
- A fila usa chaves de idempotência, leases temporários, hash do token de lease e limite de tentativas.
- Ações permitidas na fila são somente `propose_improvement` e `record_checkpoint`.
- O worker foi ajustado para validar payloads, alinhar `run_id` com a tarefa e rejeitar ações/payloads inválidos.
- Foram adicionados testes unitários para validação de payloads do worker.

## Ainda não verificado / bloqueadores
- Os novos testes ainda não foram executados neste checkpoint.
- O ciclo autenticado enqueue → claim → worker → finish ainda não foi validado de ponta a ponta.
- O worker é um processo separado e **não está configurado como serviço contínuo**.
- A implantação Vercel precisa ser conferida após os commits recentes; não presumir que o código mais novo já está publicado.
- Não há execução arbitrária de código, autoedição de fonte ou publicação automática habilitada.
- As propostas de evolução são propostas, não mudanças automáticas.

## Próximos critérios de conclusão operacional
1. Executar a suíte de testes.
2. Implantar a revisão atual e confirmar o commit na Vercel.
3. Validar health e OpenAPI da implantação nova.
4. Fazer um teste controlado de fila usando token seguro, sem expor segredo nem payload privado.
5. Confirmar resultado persistido, repetição idempotente e recuperação de falha.
6. Só então configurar um worker externo supervisionado, com limite de tarefas e logs sem segredos.

## Segurança e custos
- Nenhum segredo deve ser commitado no GitHub ou impresso em logs.
- Sem GitHub Actions; a implantação pode ser feita pelo vínculo Git da Vercel.
- Não habilitar loops infinitos nem execução arbitrária.

## Atualização operacional — 2026-10-25
- Implantação de produção confirmada como `READY`: commit `731db450ede8012df290894cf939aa36b6ee1d53` (inclui verificação real de conectividade PostgreSQL no health e smoke test somente leitura).
- O build da Vercel concluiu em aproximadamente 6 segundos; estado final consultado: `READY`.
- Novo endpoint `/api/health` agora distingue `database_configured` de `database_reachable` e nunca retorna DSN nem detalhes internos do provedor.
- Criado `scripts/smoke_test.py`, que verifica apenas `/`, `/api/health` e `/openapi.json`; não grava memória nem reivindica tarefas.
- Limitação de validação: a leitura HTTP pública foi bloqueada pela proteção SSO da Vercel; por isso, o smoke test ainda não foi executado contra o endpoint implantado.
- Bloqueio de produção: `DATABASE_URL` e `NOVACOMP_API_TOKEN` existem apenas em Preview; não há variáveis Production visíveis.
- Tentativa de criar um projeto Neon dedicado foi recusada pela política da organização gerenciada pela Vercel. Não foi usado o banco compartilhado de Arte Harum/Chat para a NovaComp, evitando mistura de dados.
- Worker externo continua sem serviço contínuo. Ollama/modelo local não está instalado nesta infraestrutura serverless.
- Nenhum segredo foi exibido ou gravado no repositório; nenhuma ação de fila foi executada em produção.

## Próximo passo obrigatório para conclusão real
1. Criar/autorizar um banco PostgreSQL dedicado à NovaComp em um projeto Neon separado, ou fornecer um endpoint de banco de produção já aprovado.
2. Adicionar `DATABASE_URL` e gerar `NOVACOMP_API_TOKEN` em Vercel → Settings → Environment Variables → Production.
3. Fazer novo deploy para aplicar as variáveis e executar `scripts/smoke_test.py` em ambiente que tenha acesso ao endpoint.
4. Hospedar `nova_worker.py` em um serviço de worker contínuo/cron supervisionado e validar o ciclo de fila com uma tarefa de teste inofensiva.
