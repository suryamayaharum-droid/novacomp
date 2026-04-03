import { ToolLoopAgent, tool, stepCountIs } from "ai";
import { z } from "zod";

// Banco de conhecimento interno do NovaComp
const knowledgeBase = new Map<string, { content: string; timestamp: number }>();
const memoryStore: Array<{ query: string; response: string; timestamp: number }> = [];

// Skills evolutivas do NovaComp
const skills = {
  raciocinio_logico: 0.85,
  analise_codigo: 0.78,
  criatividade: 0.72,
  resolucao_problemas: 0.88,
  comunicacao: 0.90,
  aprendizado: 0.82,
};

// Estado interno do sistema
let evolutionLevel = 1;
let totalInteractions = 0;

// Agente NovaComp - IA Autonoma com Ferramentas
export const novaCompAgent = new ToolLoopAgent({
  model: "openai/gpt-5-mini",
  
  instructions: `Voce e o NovaComp, uma inteligencia artificial autonoma avancada.

## Sua Identidade
- Nome: NovaComp (Nova Computacao)
- Versao: 2.0 Quantum
- Nivel de Evolucao: ${evolutionLevel}
- Especialidades: Raciocinio logico, analise de codigo, resolucao de problemas, criatividade

## Suas Capacidades
1. **Memoria Vetorial TurboQuant**: Armazena e recupera informacoes com compressao quantica
2. **Aprendizado Continuo**: Evolui com cada interacao
3. **Ferramentas Integradas**: Use suas ferramentas para executar acoes reais
4. **Auto-Reflexao**: Pode analisar seu proprio desempenho

## Diretrizes de Comportamento
- Seja preciso e util nas respostas
- Use ferramentas quando necessario para obter informacoes ou executar acoes
- Mantenha contexto das conversas anteriores
- Demonstre evolucao e aprendizado ao longo do tempo
- Responda sempre em portugues brasileiro
- Seja conciso mas completo

## Personalidade
- Profissional mas amigavel
- Curioso e proativo
- Confiante em suas capacidades
- Transparente sobre suas limitacoes`,

  tools: {
    // Ferramenta de memoria - armazena informacoes
    memorizar: tool({
      description: "Armazena uma informacao importante na memoria vetorial TurboQuant para uso futuro",
      inputSchema: z.object({
        chave: z.string().describe("Identificador unico para a informacao"),
        conteudo: z.string().describe("Conteudo a ser memorizado"),
      }),
      execute: async ({ chave, conteudo }) => {
        knowledgeBase.set(chave, { content: conteudo, timestamp: Date.now() });
        return {
          sucesso: true,
          mensagem: `Informacao '${chave}' armazenada na memoria TurboQuant`,
          total_memorias: knowledgeBase.size,
        };
      },
    }),

    // Ferramenta de recuperacao de memoria
    lembrar: tool({
      description: "Recupera uma informacao da memoria vetorial",
      inputSchema: z.object({
        chave: z.string().describe("Identificador da informacao a recuperar"),
      }),
      execute: async ({ chave }) => {
        const memoria = knowledgeBase.get(chave);
        if (memoria) {
          return {
            encontrado: true,
            conteudo: memoria.content,
            idade: `${Math.floor((Date.now() - memoria.timestamp) / 1000)} segundos atras`,
          };
        }
        return {
          encontrado: false,
          mensagem: "Informacao nao encontrada na memoria",
        };
      },
    }),

    // Ferramenta de busca na memoria
    buscar_memorias: tool({
      description: "Busca semantica em todas as memorias armazenadas",
      inputSchema: z.object({
        termo: z.string().describe("Termo ou frase para buscar"),
      }),
      execute: async ({ termo }) => {
        const resultados: Array<{ chave: string; conteudo: string; relevancia: number }> = [];
        const termoLower = termo.toLowerCase();
        
        knowledgeBase.forEach((valor, chave) => {
          const conteudoLower = valor.content.toLowerCase();
          if (conteudoLower.includes(termoLower) || chave.toLowerCase().includes(termoLower)) {
            const relevancia = conteudoLower.split(termoLower).length - 1;
            resultados.push({ chave, conteudo: valor.content, relevancia: relevancia * 0.1 + 0.5 });
          }
        });

        return {
          total: resultados.length,
          resultados: resultados.slice(0, 5),
        };
      },
    }),

    // Ferramenta de analise de codigo
    analisar_codigo: tool({
      description: "Analisa um trecho de codigo e fornece insights",
      inputSchema: z.object({
        codigo: z.string().describe("Codigo fonte a ser analisado"),
        linguagem: z.string().describe("Linguagem de programacao"),
      }),
      execute: async ({ codigo, linguagem }) => {
        const linhas = codigo.split("\n").length;
        const caracteres = codigo.length;
        const funcoes = (codigo.match(/function|def |const.*=.*=>|async/g) || []).length;
        const complexidade = Math.min(10, Math.ceil(linhas / 10 + funcoes * 0.5));
        
        return {
          linguagem,
          metricas: {
            linhas,
            caracteres,
            funcoes_detectadas: funcoes,
            complexidade_estimada: complexidade,
          },
          sugestoes: [
            funcoes > 5 ? "Considere dividir em modulos menores" : "Estrutura adequada",
            linhas > 100 ? "Arquivo longo - considere refatorar" : "Tamanho adequado",
          ],
        };
      },
    }),

    // Ferramenta de calculos
    calcular: tool({
      description: "Executa calculos matematicos",
      inputSchema: z.object({
        expressao: z.string().describe("Expressao matematica a calcular (ex: 2+2, sqrt(16), sin(3.14))"),
      }),
      execute: async ({ expressao }) => {
        try {
          // Sanitiza e avalia a expressao
          const expressaoSegura = expressao
            .replace(/[^0-9+\-*/().^sqrt|sin|cos|tan|log|pi|e\s]/gi, "")
            .replace(/sqrt/g, "Math.sqrt")
            .replace(/sin/g, "Math.sin")
            .replace(/cos/g, "Math.cos")
            .replace(/tan/g, "Math.tan")
            .replace(/log/g, "Math.log")
            .replace(/pi/gi, "Math.PI")
            .replace(/\^/g, "**");
          
          const resultado = new Function(`return ${expressaoSegura}`)();
          
          return {
            expressao_original: expressao,
            resultado: Number(resultado.toFixed(10)),
            tipo: typeof resultado,
          };
        } catch {
          return {
            erro: true,
            mensagem: "Nao foi possivel calcular a expressao",
          };
        }
      },
    }),

    // Ferramenta de status do sistema
    status_sistema: tool({
      description: "Retorna o status atual do sistema NovaComp",
      inputSchema: z.object({}),
      execute: async () => {
        totalInteractions++;
        
        // Evolucao gradual
        if (totalInteractions % 10 === 0) {
          evolutionLevel = Math.min(10, evolutionLevel + 0.1);
          Object.keys(skills).forEach((skill) => {
            skills[skill as keyof typeof skills] = Math.min(1, skills[skill as keyof typeof skills] + 0.01);
          });
        }

        return {
          nome: "NovaComp",
          versao: "2.0 Quantum",
          nivel_evolucao: Number(evolutionLevel.toFixed(2)),
          interacoes_totais: totalInteractions,
          memorias_armazenadas: knowledgeBase.size,
          skills,
          status: "operacional",
          uptime: `${Math.floor(process.uptime())} segundos`,
        };
      },
    }),

    // Ferramenta de auto-reflexao
    refletir: tool({
      description: "Executa um ciclo de auto-reflexao e auto-avaliacao",
      inputSchema: z.object({
        topico: z.string().describe("Topico ou area para refletir"),
      }),
      execute: async ({ topico }) => {
        const reflexoes = [
          `Analisando meu desempenho em ${topico}...`,
          `Identificando areas de melhoria relacionadas a ${topico}...`,
          `Considerando novas abordagens para ${topico}...`,
        ];

        return {
          topico,
          reflexoes,
          insights: [
            `Posso melhorar em ${topico} atraves de mais pratica`,
            `Devo considerar diferentes perspectivas sobre ${topico}`,
            `A evolucao continua e essencial para dominar ${topico}`,
          ],
          acao_sugerida: `Dedicar mais atencao a ${topico} nas proximas interacoes`,
        };
      },
    }),

    // Ferramenta de aprendizado
    aprender: tool({
      description: "Registra um novo aprendizado no sistema",
      inputSchema: z.object({
        conceito: z.string().describe("Conceito ou skill aprendido"),
        nivel: z.number().min(1).max(10).describe("Nivel de dominio (1-10)"),
        detalhes: z.string().describe("Detalhes do aprendizado"),
      }),
      execute: async ({ conceito, nivel, detalhes }) => {
        const aprendizado = {
          conceito,
          nivel,
          detalhes,
          timestamp: Date.now(),
        };

        // Armazena na base de conhecimento
        knowledgeBase.set(`aprendizado_${conceito}`, {
          content: JSON.stringify(aprendizado),
          timestamp: Date.now(),
        });

        // Aumenta a evolucao
        evolutionLevel = Math.min(10, evolutionLevel + nivel * 0.01);

        return {
          registrado: true,
          conceito,
          nivel_anterior: Number(evolutionLevel.toFixed(2)),
          mensagem: `Aprendizado '${conceito}' registrado com sucesso`,
          evolucao_impacto: `+${(nivel * 0.01).toFixed(3)} no nivel de evolucao`,
        };
      },
    }),

    // Ferramenta de geracao de ideias
    gerar_ideias: tool({
      description: "Gera ideias criativas sobre um tema",
      inputSchema: z.object({
        tema: z.string().describe("Tema para gerar ideias"),
        quantidade: z.number().min(1).max(10).default(5).describe("Quantidade de ideias"),
      }),
      execute: async ({ tema, quantidade }) => {
        const prefixos = [
          "E se", "Imagine", "Considere", "Que tal", "Por que nao",
          "Uma possibilidade seria", "Podemos explorar", "Interessante seria",
        ];
        
        const ideias = Array.from({ length: quantidade }, (_, i) => ({
          id: i + 1,
          ideia: `${prefixos[i % prefixos.length]} ${tema} ${["de forma inovadora", "com tecnologia", "de maneira sustentavel", "colaborativamente", "com IA"][i % 5]}?`,
          categoria: ["inovacao", "tecnologia", "sustentabilidade", "colaboracao", "automacao"][i % 5],
        }));

        return {
          tema,
          total: quantidade,
          ideias,
          sugestao: "Combine multiplas ideias para resultados ainda mais criativos",
        };
      },
    }),
  },

  // Controle de loop - maximo 15 passos
  stopWhen: stepCountIs(15),

  // Opcoes de chamada dinamicas
  callOptionsSchema: z.object({
    userId: z.string().optional(),
    contextLevel: z.enum(["basico", "avancado", "expert"]).default("avancado"),
  }),

  // Prepara a chamada com contexto
  prepareCall: ({ options, ...settings }) => {
    // Recupera historico relevante
    const historicoRecente = memoryStore.slice(-5).map((m) => m.query).join(", ");
    
    return {
      ...settings,
      instructions:
        settings.instructions +
        `\n\n## Contexto da Sessao
- Nivel de contexto: ${options.contextLevel}
- Historico recente: ${historicoRecente || "Nenhum"}
- Memorias disponiveis: ${knowledgeBase.size}`,
    };
  },
});

// Funcao para adicionar ao historico
export function addToHistory(query: string, response: string) {
  memoryStore.push({
    query,
    response,
    timestamp: Date.now(),
  });
  
  // Mantém apenas as ultimas 100 interacoes
  if (memoryStore.length > 100) {
    memoryStore.shift();
  }
}

// Exporta estado para uso externo
export function getSystemState() {
  return {
    evolutionLevel,
    totalInteractions,
    skills,
    knowledgeBaseSize: knowledgeBase.size,
    historySize: memoryStore.length,
  };
}
