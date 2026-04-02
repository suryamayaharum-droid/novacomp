"""
NovaComp - Interface Web e Dashboard
Renderização em tempo real dos processos da IA no navegador
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn

from core.brain import NovaCompCore
from agents.executor import TaskExecutorAgent


# Aplicações FastAPI
app = FastAPI(title="NovaComp AI", description="Interface da Inteligência Autônoma")

# CORS para acesso do navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Instâncias globais
nova_core: Optional[NovaCompCore] = None
executor_agent: Optional[TaskExecutorAgent] = None
connected_clients: List[WebSocket] = []


def initialize_system():
    """Inicializa o sistema NovaComp"""
    global nova_core, executor_agent
    
    nova_core = NovaCompCore(name="NovaComp-Alpha")
    executor_agent = TaskExecutorAgent(safe_mode=True)
    
    # Registra agente no core
    nova_core.register_agent("executor", executor_agent.execute)
    
    return nova_core, executor_agent


# Template HTML do dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaComp - IA Autônoma Viva</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #0f3460;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            background: linear-gradient(90deg, #e94560, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 20px;
            background: #0f3460;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(15, 52, 96, 0.5);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid #0f3460;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h2 {
            color: #e94560;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: bold;
            color: #4ade80;
        }
        
        .skill-bar {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            height: 8px;
            margin-top: 5px;
            overflow: hidden;
        }
        
        .skill-fill {
            height: 100%;
            background: linear-gradient(90deg, #e94560, #ff6b6b);
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        .log-container {
            background: #0d1117;
            border-radius: 10px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }
        
        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .log-timestamp {
            color: #8b949e;
        }
        
        .log-info { color: #58a6ff; }
        .log-success { color: #3fb950; }
        .log-warning { color: #d29922; }
        .log-error { color: #f85149; }
        
        .input-section {
            background: rgba(15, 52, 96, 0.5);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        textarea {
            width: 100%;
            min-height: 100px;
            background: #0d1117;
            border: 1px solid #0f3460;
            border-radius: 10px;
            color: #eee;
            padding: 15px;
            font-size: 1em;
            resize: vertical;
        }
        
        textarea:focus {
            outline: none;
            border-color: #e94560;
        }
        
        button {
            background: linear-gradient(90deg, #e94560, #ff6b6b);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s ease;
        }
        
        button:hover {
            transform: scale(1.05);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .evolution-level {
            font-size: 3em;
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(90deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .process-viz {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .process-node {
            flex: 1;
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-size: 0.8em;
        }
        
        .process-node.active {
            background: rgba(74, 222, 128, 0.2);
            border: 1px solid #4ade80;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 NovaComp</h1>
            <p style="color: #8b949e; margin-bottom: 15px;">Inteligência Autônoma Viva</p>
            <div class="status-badge">
                <span class="status-indicator"></span>
                <span id="connection-status">Conectado</span>
            </div>
        </header>
        
        <div class="input-section">
            <h2>💬 Interaja com a IA</h2>
            <textarea id="user-input" placeholder="Digite sua mensagem ou comando para NovaComp..."></textarea>
            <button onclick="sendMessage()" id="send-btn">Enviar</button>
        </div>
        
        <div class="evolution-level">
            Nível <span id="evo-level">1</span>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📊 Status do Sistema</h2>
                <div class="metric">
                    <span>Estado:</span>
                    <span class="metric-value" id="state">idle</span>
                </div>
                <div class="metric">
                    <span>Tempo ativo:</span>
                    <span class="metric-value" id="uptime">0h</span>
                </div>
                <div class="metric">
                    <span>Memórias:</span>
                    <span class="metric-value" id="memories">0</span>
                </div>
                <div class="metric">
                    <span>Eventos de aprendizado:</span>
                    <span class="metric-value" id="learning-events">0</span>
                </div>
                
                <h3 style="margin-top: 20px; color: #e94560;">Processos</h3>
                <div class="process-viz">
                    <div class="process-node" id="proc-thinking">Pensando</div>
                    <div class="process-node" id="proc-learning">Aprendendo</div>
                    <div class="process-node" id="proc-executing">Executando</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Habilidades</h2>
                <div id="skills-container">
                    <!-- Skills serão inseridas via JS -->
                </div>
            </div>
            
            <div class="card">
                <h2>📝 Memória</h2>
                <div class="metric">
                    <span>Total memórias:</span>
                    <span class="metric-value" id="total-memories">0</span>
                </div>
                <div class="metric">
                    <span>Relações:</span>
                    <span class="metric-value" id="total-relations">0</span>
                </div>
                <div class="metric">
                    <span>Cache curto prazo:</span>
                    <span class="metric-value" id="cache-size">0</span>
                </div>
                <div class="metric">
                    <span>Acessos recentes:</span>
                    <span class="metric-value" id="recent-accesses">0</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📜 Logs em Tempo Real</h2>
            <div class="log-container" id="log-container">
                <div class="log-entry">
                    <span class="log-timestamp">[--:--:--]</span>
                    <span class="log-info">Sistema inicializado...</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws;
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                document.getElementById('connection-status').textContent = 'Conectado';
                addLog('success', 'Conectado ao servidor NovaComp');
            };
            
            ws.onclose = () => {
                document.getElementById('connection-status').textContent = 'Desconectado';
                addLog('error', 'Desconectado. Reconectando...');
                setTimeout(connect, 3000);
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onerror = (error) => {
                addLog('error', 'Erro na conexão WebSocket');
            };
        }
        
        function addLog(level, message) {
            const container = document.getElementById('log-container');
            const timestamp = new Date().toLocaleTimeString();
            
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `
                <span class="log-timestamp">[${timestamp}]</span>
                <span class="log-${level}">${message}</span>
            `;
            
            container.insertBefore(entry, container.firstChild);
            
            // Mantém apenas 100 logs
            while (container.children.length > 100) {
                container.removeChild(container.lastChild);
            }
        }
        
        function updateDashboard(data) {
            if (data.type === 'status_update') {
                const status = data.data;
                
                document.getElementById('state').textContent = status.state;
                document.getElementById('uptime').textContent = status.uptime_hours.toFixed(2) + 'h';
                document.getElementById('evo-level').textContent = status.evolution_level;
                document.getElementById('learning-events').textContent = status.learning_events;
                
                // Atualiza processos
                document.getElementById('proc-thinking').classList.toggle('active', status.state === 'thinking');
                document.getElementById('proc-learning').classList.toggle('active', status.state === 'learning');
                document.getElementById('proc-executing').classList.toggle('active', status.state === 'executing');
                
                // Atualiza skills
                const skillsContainer = document.getElementById('skills-container');
                skillsContainer.innerHTML = '';
                
                for (const [skill, value] of Object.entries(status.skills)) {
                    const skillDiv = document.createElement('div');
                    skillDiv.style.marginBottom = '12px';
                    skillDiv.innerHTML = `
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span>${skill}</span>
                            <span style="color: #4ade80;">${(value * 100).toFixed(1)}%</span>
                        </div>
                        <div class="skill-bar">
                            <div class="skill-fill" style="width: ${value * 100}%"></div>
                        </div>
                    `;
                    skillsContainer.appendChild(skillDiv);
                }
                
                // Atualiza memória
                if (status.memory_stats) {
                    document.getElementById('memories').textContent = status.memory_stats.total_memories;
                    document.getElementById('total-memories').textContent = status.memory_stats.total_memories;
                    document.getElementById('total-relations').textContent = status.memory_stats.total_relations;
                    document.getElementById('cache-size').textContent = status.memory_stats.short_term_cache_size;
                    document.getElementById('recent-accesses').textContent = status.memory_stats.recent_accesses;
                }
            }
            
            if (data.type === 'log') {
                addLog(data.level || 'info', data.message);
            }
            
            if (data.type === 'response') {
                addLog('success', 'Resposta: ' + JSON.stringify(data.data).substring(0, 100));
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const btn = document.getElementById('send-btn');
            const message = input.value.trim();
            
            if (!message || !ws || ws.readyState !== WebSocket.OPEN) {
                return;
            }
            
            btn.disabled = true;
            addLog('info', 'Enviando: ' + message);
            
            try {
                const response = await fetch('/api/think', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input: message })
                });
                
                const result = await response.json();
                addLog('success', 'Resposta recebida');
                
                ws.send(JSON.stringify({
                    type: 'user_message',
                    data: { input: message, response: result }
                }));
                
            } catch (error) {
                addLog('error', 'Erro: ' + error.message);
            } finally {
                btn.disabled = false;
                input.value = '';
            }
        }
        
        // Conecta ao carregar
        connect();
        
        // Atualização periódica
        setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 10000);
    </script>
</body>
</html>
"""


@app.get("/")
async def root():
    """Serve o dashboard"""
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/dashboard")
async def dashboard():
    """Alias para o dashboard"""
    return HTMLResponse(content=DASHBOARD_HTML)


@app.post("/api/think")
async def api_think(request: dict):
    """Processa entrada do usuário"""
    
    if not nova_core:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    input_text = request.get("input", "")
    context = request.get("context", {})
    
    # Processa pensamento
    decision = await nova_core.think(input_text, context)
    
    # Broadcast para clientes WebSocket
    await broadcast_to_clients({
        "type": "response",
        "data": decision
    })
    
    return decision


@app.post("/api/learn")
async def api_learn(request: dict):
    """Ensina novo conhecimento à IA"""
    
    if not nova_core:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    knowledge = request.get("knowledge", {})
    
    result = await nova_core.learn(knowledge)
    
    await broadcast_to_clients({
        "type": "log",
        "level": "success",
        "message": f"Novo conhecimento aprendido: {knowledge.get('type', 'unknown')}"
    })
    
    return result


@app.get("/api/status")
async def api_status():
    """Retorna status do sistema"""
    
    if not nova_core:
        raise HTTPException(status_code=500, detail="Sistema não inicializado")
    
    return nova_core.get_status()


@app.post("/api/execute")
async def api_execute(request: dict):
    """Executa comando seguro"""
    
    if not executor_agent:
        raise HTTPException(status_code=500, detail="Agente não inicializado")
    
    command = request.get("command", "")
    timeout = request.get("timeout", 30)
    
    result = await executor_agent.execute(command, timeout)
    
    return result


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para atualizações em tempo real"""
    
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                # Envia status atual
                if nova_core:
                    status = nova_core.get_status()
                    await websocket.send_json({
                        "type": "status_update",
                        "data": status
                    })
            
            elif message.get("type") == "user_message":
                await websocket.send_json({
                    "type": "log",
                    "level": "info",
                    "message": "Mensagem processada"
                })
    
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        await broadcast_to_clients({
            "type": "log",
            "level": "info",
            "message": "Cliente desconectado"
        })


async def broadcast_to_clients(message: dict):
    """Envia mensagem para todos os clientes conectados"""
    
    disconnected = []
    
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            disconnected.append(client)
    
    # Remove clientes desconectados
    for client in disconnected:
        if client in connected_clients:
            connected_clients.remove(client)


@app.on_event("startup")
async def startup_event():
    """Inicializa sistema ao iniciar"""
    
    initialize_system()
    
    # Inicia tarefa de atualização periódica
    asyncio.create_task(periodic_status_update())
    
    print("\n🚀 NovaComp inicializado!")
    print("🌐 Acesse: http://localhost:8000/dashboard\n")


async def periodic_status_update():
    """Envia atualizações periódicas para clientes"""
    
    while True:
        await asyncio.sleep(5)  # A cada 5 segundos
        
        if nova_core and connected_clients:
            status = nova_core.get_status()
            await broadcast_to_clients({
                "type": "status_update",
                "data": status
            })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
