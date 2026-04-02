#!/usr/bin/env python3
"""
NovaComp - Dashboard Web em Tempo Real
Interface visual para monitoramento e interação com a IA
"""

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import sys
import json
from datetime import datetime
from pathlib import Path
import threading
import time

# Adicionar caminho do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.brain import NovaBrain
from memory.turboquant import TurboQuantMemory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'novacomp-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Instância global do brain
brain = None
running = False

# Template HTML embutido
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaComp Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #0f3460;
            margin-bottom: 30px;
        }
        h1 { 
            font-size: 2.5em; 
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .status-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }
        .status-active { background: #00ff88; color: #000; }
        .status-idle { background: #ffd700; color: #000; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        .card h2 {
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #00d9ff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .stat-value { font-weight: bold; color: #00ff88; }
        .skill-bar {
            margin: 15px 0;
        }
        .skill-name { 
            display: flex; 
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        .progress-bg {
            background: rgba(255, 255, 255, 0.1);
            height: 10px;
            border-radius: 5px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            border-radius: 5px;
            transition: width 0.5s ease;
        }
        .chat-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            height: 300px;
            overflow-y: auto;
            margin-bottom: 15px;
        }
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 10px;
            max-width: 80%;
        }
        .message.user {
            background: #0f3460;
            margin-left: auto;
        }
        .message.ai {
            background: rgba(0, 217, 255, 0.2);
            border-left: 3px solid #00d9ff;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 1em;
        }
        input[type="text"]:focus {
            outline: 2px solid #00d9ff;
        }
        button {
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            color: #000;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.05); }
        .log-entry {
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .log-time { color: #888; }
        .thinking-indicator {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .thinking-indicator.active { display: block; }
        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        .pulse { animation: pulse 1.5s infinite; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 NovaComp Dashboard</h1>
            <p>Sistema de IA Autônoma Viva - Monitoramento em Tempo Real</p>
            <span id="statusBadge" class="status-badge status-idle">⏸️ Idle</span>
        </header>

        <div class="grid">
            <!-- Status Card -->
            <div class="card">
                <h2>📊 Status do Sistema</h2>
                <div id="systemStats">
                    <div class="stat-item">
                        <span>Nível de Evolução:</span>
                        <span class="stat-value" id="evoLevel">1</span>
                    </div>
                    <div class="stat-item">
                        <span>Experiência (XP):</span>
                        <span class="stat-value" id="xpPoints">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Memórias Armazenadas:</span>
                        <span class="stat-value" id="memoryCount">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Pensamentos:</span>
                        <span class="stat-value" id="thoughtCount">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Tempo Ativo:</span>
                        <span class="stat-value" id="uptime">00:00:00</span>
                    </div>
                </div>
            </div>

            <!-- Skills Card -->
            <div class="card">
                <h2>🎯 Habilidades Cognitivas</h2>
                <div id="skillsContainer">
                    <!-- Preenchido via JavaScript -->
                </div>
            </div>

            <!-- Chat Card -->
            <div class="card" style="grid-column: span 2;">
                <h2>💬 Interagir com NovaComp</h2>
                <div class="chat-container" id="chatContainer">
                    <div class="message ai">
                        🤖 Olá! Sou o NovaComp. Como posso ajudar você hoje?
                    </div>
                </div>
                <div class="thinking-indicator" id="thinkingIndicator">
                    <span class="pulse">💭 NovaComp está pensando...</span>
                </div>
                <div class="input-group">
                    <input type="text" id="userInput" placeholder="Digite sua mensagem..." 
                           onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()">Enviar</button>
                </div>
            </div>

            <!-- Logs Card -->
            <div class="card" style="grid-column: span 2;">
                <h2>📜 Logs em Tempo Real</h2>
                <div id="logsContainer" style="height: 200px; overflow-y: auto;">
                    <!-- Logs preenchidos via WebSocket -->
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        const chatContainer = document.getElementById('chatContainer');
        const logsContainer = document.getElementById('logsContainer');
        const thinkingIndicator = document.getElementById('thinkingIndicator');
        const statusBadge = document.getElementById('statusBadge');

        // Conectar ao WebSocket
        socket.on('connect', () => {
            addLog('✅ Conectado ao NovaComp');
            updateStatus();
        });

        socket.on('status_update', (data) => {
            updateSystemStats(data);
        });

        socket.on('ai_response', (data) => {
            thinkingIndicator.classList.remove('active');
            addMessage(data.response, 'ai');
            addLog(`🧠 Resposta gerada (${data.intention})`);
        });

        socket.on('thinking', (data) => {
            thinkingIndicator.classList.add('active');
            statusBadge.className = 'status-badge status-active';
            statusBadge.textContent = '💭 Thinking';
        });

        socket.on('idle', () => {
            statusBadge.className = 'status-badge status-idle';
            statusBadge.textContent = '⏸️ Idle';
        });

        socket.on('log', (data) => {
            addLog(data.message);
        });

        function updateSystemStats(data) {
            document.getElementById('evoLevel').textContent = data.evolution_level;
            document.getElementById('xpPoints').textContent = data.experience_points;
            document.getElementById('memoryCount').textContent = data.memory_stats.total_memories;
            document.getElementById('thoughtCount').textContent = data.thought_count;
            document.getElementById('uptime').textContent = data.uptime;

            // Atualizar barras de habilidade
            const skillsContainer = document.getElementById('skillsContainer');
            skillsContainer.innerHTML = '';
            
            for (const [skill, value] of Object.entries(data.skills)) {
                const skillDiv = document.createElement('div');
                skillDiv.className = 'skill-bar';
                skillDiv.innerHTML = `
                    <div class="skill-name">
                        <span>${skill.charAt(0).toUpperCase() + skill.slice(1)}</span>
                        <span>${value}/100</span>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill" style="width: ${value}%"></div>
                    </div>
                `;
                skillsContainer.appendChild(skillDiv);
            }
        }

        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => updateSystemStats(data));
        }

        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            
            socket.emit('user_message', { text: message });
        }

        function addMessage(text, type) {
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = text;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function addLog(message) {
            const div = document.createElement('div');
            div.className = 'log-entry';
            const time = new Date().toLocaleTimeString();
            div.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
            logsContainer.appendChild(div);
            logsContainer.scrollTop = logsContainer.scrollHeight;
        }

        // Atualizar status periodicamente
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
"""

def background_worker():
    """Worker em segundo plano para atualizações"""
    global running
    while running:
        try:
            if brain:
                status = brain.get_status()
                socketio.emit('status_update', status)
        except Exception as e:
            print(f"Erro no worker: {e}")
        time.sleep(3)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    if brain:
        return jsonify(brain.get_status())
    return jsonify({'error': 'Brain not initialized'})

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    emit('log', {'message': 'Novo cliente conectado'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

@socketio.on('user_message')
def handle_message(data):
    if not brain:
        emit('ai_response', {'response': 'Sistema não inicializado', 'intention': 'error'})
        return
    
    text = data.get('text', '')
    emit('thinking', {})
    emit('log', {'message': f'Usuário: {text}'})
    
    # Processar mensagem em thread separada
    def process():
        result = brain.think(text)
        response = result['response']
        intention = result['thought']['intention']['type']
        
        emit('ai_response', {
            'response': response.strip(),
            'intention': intention
        })
        emit('idle', {})
        emit('log', {'message': f'IA respondeu: {intention}'})
        
        # Aprender com a interação
        brain.learn({
            'summary': f'Interação: {text[:50]}',
            'outcome': 'success'
        })
    
    threading.Thread(target=process).start()

def run_dashboard(host='0.0.0.0', port=5000):
    global brain, running
    
    print("\n🌐 Iniciando NovaComp Dashboard...")
    print(f"   URL: http://localhost:{port}")
    print("   Pressione Ctrl+C para parar\n")
    
    # Inicializar brain
    brain = NovaBrain(name="NovaComp-Web")
    running = True
    
    # Iniciar worker em background
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()
    
    # Iniciar servidor Flask
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    run_dashboard()
