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
