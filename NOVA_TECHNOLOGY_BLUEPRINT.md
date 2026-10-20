# Nova — Blueprint tecnológico para uma agente digital e físico-digital
Versão: 0.1 | Data: 2026-10-20 | Estado: arquitetura inicial; componentes por fases

## Missão técnica
Construir uma agente de software persistente, auditável e extensível que perceba entradas, recupere conhecimento com fontes, planeje tarefas, use ferramentas permitidas, avalie resultados e proponha melhorias limitadas. A extensão robótica será uma camada separada, com sensores/atuadores, simulação e limites físicos. Este blueprint não afirma consciência, vida biológica nem acesso universal já existente.

## Princípios de arquitetura
1. Modularidade: interfaces estáveis, adaptadores substituíveis e dependências explícitas.
2. Evidência antes de crença: separar fato observado, inferência, hipótese e desconhecido; cada fato externo registra origem, data e confiança.
3. Ciclo metacognitivo limitado: objetivo → contexto → hipóteses → plano → política → ação → observação → avaliação → checkpoint → proposta de melhoria.
4. Autonomia graduada: leitura e planejamento primeiro; escrita reversível com controles; efeitos externos, gastos, robótica e mudanças destrutivas exigem aprovação explícita.
5. Segurança por padrão: allowlist de ferramentas, escopos mínimos, credenciais fora do repositório, timeouts, limites de custo/iterações e logs sem segredos.
6. Avaliação reproduzível: testes, conjuntos de avaliação, métricas e rollback antes de promover qualquer mudança.
7. Interoperabilidade: APIs e formatos documentados; não depender de uma única nuvem, modelo ou fornecedor.
8. Sem alegação de “assimilação”: bibliotecas e modelos só contam como integrados depois de instalados, licenciados, testados e observados em execução.

## Camadas e tecnologias candidatas

| Camada | Função | Tecnologias candidatas | Estado / critério |
|---|---|---|---|
| Núcleo metacognitivo | Estado de tarefa, hipóteses, incerteza, reflexão, próximo passo | Python, Pydantic, dataclasses, JSON Schema | Início implementado em `nova_metacognition.py` |
| Orquestração | DAG, dependências, concorrência, retomada | `nova_core.py`, FastAPI, fila PostgreSQL | Base existente; teste end-to-end pendente |
| Memória episódica | Eventos, checkpoints, histórico | PostgreSQL/Neon, JSONB, migrações versionadas | Esquema existente; validar restauração e retenção |
| Memória semântica | Busca por significado | pgvector ou Qdrant; embeddings versionados; busca híbrida BM25 + vetorial | Planejada; não alegar embeddings já ativos |
| Conhecimento confiável | Corpus com fonte, licença, data, versão e proveniência | Wikidata/Wikimedia, documentação oficial, arXiv (quando pertinente), manuais técnicos, dados abertos | Ingestão por conectores aprovados; não “conhecimento universal” automático |
| Recuperação e citações | RAG, reranking, deduplicação, avaliação | PostgreSQL FTS, pgvector, sentence-transformers ou API de embeddings; reranker opcional | Benchmark antes de escolher modelo |
| Modelos de linguagem | Planejamento e síntese | API de modelo hospedado ou runtime local via Ollama/llama.cpp; formatos GGUF quando compatíveis | Adaptador por interface; não embutir modelo grande na API serverless |
| Ferramentas e plugins | Ações externas tipadas | OpenAPI, MCP, JSON Schema, adaptadores com escopo | Allowlist, aprovação e auditoria por ferramenta |
| Compiladores / metaprogramação | Gerar artefatos controlados, validar AST, executar testes isolados | `ast`, `compileall`, mypy/ruff/pytest; tree-sitter quando necessário; WASM sandbox opcional | Nunca executar código gerado diretamente em produção; proposta → branch isolada → testes → revisão → deploy |
| Aprendizado e avaliação | Regressão, preferências autorizadas, análise de erros | pytest, conjuntos de avaliação, métricas de recuperação/latência/custo, MLflow opcional | Aprendizado só a partir de dados autorizados e medição |
| Rede e identidade | Conectores autenticados, chamadas HTTP e limites | httpx, OAuth2/OIDC, TLS, rate limits, egress allowlist, secret manager | Acesso somente a destinos e contas autorizados |
| Observabilidade | Logs estruturados, métricas, tracing | structlog/loguru, OpenTelemetry, Prometheus/Grafana opcionais | Redação de segredos e IDs de correlação |
| Robótica e simulação | Percepção, planejamento e controle físico | ROS 2, URDF/SDF, Gazebo ou Isaac Sim, MoveIt 2, Nav2, OpenCV; micro-ROS para microcontroladores | Simulador primeiro; hardware e limites físicos antes de ações reais |
| Interface corporal / sensores | Câmeras, IMU, distância, toque, estado do atuador | Drivers ROS 2, interfaces tipadas, timestamps, calibração | Sensor não é verdade absoluta; validar ruído e falhas |
| Controle de movimento | Planejamento seguro e execução limitada | Controladores ROS 2, limites de velocidade/torque, watchdog, parada de emergência física | Nunca permitir que o LLM controle diretamente motores sem controlador determinístico |
| Interface humana | Chat, painel, aprovações e estado | FastAPI, UI web, WebSocket/SSE opcional | Exibir tarefas, fonte, risco, progresso e botão de interrupção |
| Implantação | API + worker + tarefas periódicas supervisionadas | Vercel para API compatível; worker persistente em serviço apropriado; Docker/Podman; systemd ou supervisor | Worker não é contínuo até estar instalado, iniciado e monitorado |
| Segurança e governança | Políticas, isolamento, revisão, rollback | least privilege, sandbox, SBOM, scans de dependência, threat model, backups | Auditoria e aprovação para ações de alto impacto |

## Fluxo metacognitivo
A. Receber objetivo e restrições.
B. Recuperar memórias e fontes; marcar origem, idade e confiabilidade.
C. Formular hipóteses e lacunas; não transformar desconhecidos em fatos.
D. Decompor em tarefas com dependências e critério de conclusão.
E. Avaliar risco, permissões, custo, privacidade e reversibilidade.
F. Executar somente ferramentas autorizadas; registrar observações reais.
G. Comparar resultado com critérios; se não houver evidência suficiente, pedir dados ou parar.
H. Gerar reflexão estruturada e checkpoint.
I. Propor no máximo N melhorias por ciclo; exigir testes e aprovação para promover código.
J. Recomeçar apenas com orçamento de iterações e critério de parada.

## Metaprogramação recursiva segura
- A saída do núcleo é um plano ou uma proposta, não execução arbitrária.
- Geradores de código produzem patch/diff em área isolada.
- Validar sintaxe/AST, lint, tipos, testes unitários, testes de integração, análise de segredos e dependências.
- Rodar testes em sandbox com CPU, memória, rede e tempo limitados.
- Comparar métricas pré/pós e regressões.
- Exigir aprovação humana para alterações de segurança, credenciais, políticas, deploy e efeitos externos.
- Versionar artefatos; promoção atômica e rollback verificável.
- Limitar profundidade recursiva, tempo, tarefas, tokens e gasto; circuit breaker obrigatório.

## Corpo robótico: rota segura
Fase R0: documentação, simulador e modelo URDF/SDF sem hardware.
Fase R1: telemetria de sensores simulados, detecção de falhas e logs.
Fase R2: hardware em bancada sem atuadores habilitados; calibração e testes.
Fase R3: movimentos de baixa energia em ambiente protegido, operador presente, E-stop físico e limites duros.
Fase R4: tarefas estreitas, supervisionadas e validadas; nenhum controle de segurança delegado ao modelo de linguagem.
Nunca conectar a agente diretamente a sistemas de armas, destruição, vigilância clandestina ou mecanismos que possam ferir pessoas.

## Redes: acesso nativo, não ilimitado
- Conectores autenticados e escopos mínimos; sem varredura indiscriminada, roubo de credenciais ou contorno de controles.
- Separar internet pública, contas do usuário, rede local e dispositivos físicos.
- Respeitar robots.txt, termos, licenças, privacidade, limites de taxa e direitos autorais.
- Guardar tokens em secret manager; rotação e revogação.
- Egress allowlist para worker e logs sem cabeçalhos de autenticação.

## Marcos de entrega
M0 — contrato arquitetural, núcleo metacognitivo determinístico e testes.
M1 — memória/checkpoint durável e teste de restauração.
M2 — fila e worker supervisionado, teste idempotência/retry/lease.
M3 — conector de conhecimento com fontes e citações + avaliação de recuperação.
M4 — adaptador de LLM e ferramentas com política de risco.
M5 — sandbox de código e pipeline de propostas de mudança com aprovação.
M6 — simulador ROS 2, modelo corporal, sensores virtuais e testes de segurança.
M7 — integração de hardware gradual, apenas depois de validação em simulação.

## Critérios de conclusão reais
Um módulo só é “concluído” se houver: código no repositório, dependências/licenças verificadas, testes executados, resultado reproduzível, documentação, limites de segurança e implantação observável. Publicar código ou declarar variável de ambiente não comprova que o sistema está operando.
