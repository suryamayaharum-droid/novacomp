"""
Módulo de Visualização Neural 3D no Navegador
Renderiza os processos de pensamento, conexões de memória e atividade vetorial.
Usa Three.js via CDN para gráficos leves e acelerados por hardware.
"""
from flask import Flask, render_template_string, jsonify
import json
import random
import math

app = Flask(__name__)

# Template HTML/JS embutido para portabilidade
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>NovaComp - Neural Visualizer</title>
    <style>
        body { margin: 0; overflow: hidden; background: #050510; color: #0ff; font-family: 'Courier New', monospace; }
        #canvas-container { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; z-index: 1; }
        #ui-layer { position: absolute; top: 20px; left: 20px; z-index: 10; pointer-events: none; }
        .panel { background: rgba(0, 20, 40, 0.8); border: 1px solid #0ff; padding: 15px; border-radius: 8px; margin-bottom: 10px; backdrop-filter: blur(5px); }
        h1 { margin: 0 0 10px 0; font-size: 1.2rem; text-shadow: 0 0 10px #0ff; }
        .stat { display: flex; justify-content: space-between; margin-bottom: 5px; }
        .val { color: #fff; font-weight: bold; }
        #log-console { position: absolute; bottom: 20px; left: 20px; right: 20px; height: 200px; z-index: 10; background: rgba(0,0,0,0.8); border-top: 2px solid #0f0; overflow-y: auto; padding: 10px; font-size: 0.9rem; }
        .log-entry { margin-bottom: 4px; border-bottom: 1px solid #333; padding-bottom: 2px; }
        .log-think { color: #ff0; }
        .log-learn { color: #0f0; }
        .log-exec { color: #f0f; }
    </style>
    <!-- Three.js via CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="ui-layer">
        <div class="panel">
            <h1>🧠 NovaComp Neural Core</h1>
            <div class="stat"><span>Status:</span> <span class="val" id="status-val">ONLINE</span></div>
            <div class="stat"><span>Neurônios Ativos:</span> <span class="val" id="neurons-val">0</span></div>
            <div class="stat"><span>Memória TurboQuant:</span> <span class="val" id="memory-val">0 MB</span></div>
            <div class="stat"><span>Ciclo de Pensamento:</span> <span class="val" id="cycle-val">Idle</span></div>
        </div>
    </div>
    
    <div id="log-console"></div>
    <div id="canvas-container"></div>

    <script>
        // Configuração Three.js
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x050510, 0.002);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 50;
        
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Criar Rede Neural (Partículas)
        const particlesGeometry = new THREE.BufferGeometry();
        const particlesCount = 300;
        const posArray = new Float32Array(particlesCount * 3);
        
        for(let i = 0; i < particlesCount * 3; i++) {
            posArray[i] = (Math.random() - 0.5) * 60; // Espalhar em 60 unidades
        }
        
        particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        
        // Material dos Neurônios
        const particlesMaterial = new THREE.PointsMaterial({
            size: 0.4,
            color: 0x00ffff,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });
        
        const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
        scene.add(particlesMesh);

        // Linhas de Conexão (Sinapses)
        const linesMaterial = new THREE.LineBasicMaterial({ color: 0x0044ff, transparent: true, opacity: 0.3 });
        const linesGeometry = new THREE.BufferGeometry();
        // Inicialmente vazio, atualizado dinamicamente
        
        let connectionsMesh = new THREE.LineSegments(linesGeometry, linesMaterial);
        scene.add(connectionsMesh);

        // Animação
        let time = 0;
        function animate() {
            requestAnimationFrame(animate);
            time += 0.01;
            
            particlesMesh.rotation.y = time * 0.1;
            particlesMesh.rotation.x = time * 0.05;
            
            // Pulsar partículas
            const positions = particlesGeometry.attributes.position.array;
            for(let i = 0; i < particlesCount; i++) {
                const i3 = i * 3;
                // Movimento suave senoidal
                positions[i3 + 1] += Math.sin(time + positions[i3]) * 0.02; 
            }
            particlesGeometry.attributes.position.needsUpdate = true;

            // Atualizar conexões dinâmicas (simulação de pensamento)
            updateConnections();

            controls.update();
            renderer.render(scene, camera);
        }
        
        function updateConnections() {
            // Lógica simplificada: conectar pontos próximos
            const positions = particlesGeometry.attributes.position.array;
            const linePositions = [];
            const maxDist = 12.0;
            
            for (let i = 0; i < particlesCount; i++) {
                for (let j = i + 1; j < particlesCount; j++) {
                    const dx = positions[i*3] - positions[j*3];
                    const dy = positions[i*3+1] - positions[j*3+1];
                    const dz = positions[i*3+2] - positions[j*3+2];
                    const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                    
                    if (dist < maxDist) {
                        linePositions.push(
                            positions[i*3], positions[i*3+1], positions[i*3+2],
                            positions[j*3], positions[j*3+1], positions[j*3+2]
                        );
                    }
                }
            }
            
            connectionsMesh.geometry.dispose();
            connectionsMesh.geometry = new THREE.BufferGeometry();
            connectionsMesh.geometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
        }

        // Simular dados vindos do backend (Polling)
        async function fetchData() {
            try {
                const response = await fetch('/api/neural_state');
                const data = await response.json();
                
                document.getElementById('neurons-val').innerText = data.active_neurons;
                document.getElementById('memory-val').innerText = data.memory_usage_mb + " MB";
                document.getElementById('cycle-val').innerText = data.current_cycle;
                
                addLog(data.last_action, data.action_type);
                
                // Mudar cor baseado no estado
                if(data.current_cycle === 'THINKING') particlesMaterial.color.setHex(0xffff00);
                else if(data.current_cycle === 'LEARNING') particlesMaterial.color.setHex(0x00ff00);
                else particlesMaterial.color.setHex(0x00ffff);
                
            } catch (e) { console.log("Aguardando backend..."); }
        }
        
        function addLog(msg, type) {
            const consoleDiv = document.getElementById('log-console');
            const entry = document.createElement('div');
            entry.className = 'log-entry log-' + (type || 'think');
            entry.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
            consoleDiv.prepend(entry);
            if(consoleDiv.children.length > 50) consoleDiv.lastChild.remove();
        }

        setInterval(fetchData, 1000); // Atualizar a cada segundo
        animate();
        
        // Resize handler
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/neural_state')
def get_neural_state():
    # Simulação de dados que viriam do Brain/Memory
    # Em produção, isso leria o estado real do objeto Brain
    return jsonify({
        "active_neurons": random.randint(50, 300),
        "memory_usage_mb": round(random.uniform(12.5, 45.0), 2),
        "current_cycle": random.choice(["IDLE", "THINKING", "LEARNING", "EXECUTING"]),
        "last_action": "Otimizando vetores de memória...",
        "action_type": random.choice(["think", "learn", "exec"])
    })

if __name__ == '__main__':
    print("🚀 Iniciando Visualizador Neural em http://localhost:5000")
    app.run(debug=True, port=5000)
