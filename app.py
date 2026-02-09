#!/usr/bin/env python3
"""
🌐 INTERFAZ WEB PARA LINKEDIN BOT
Versión: 1.0 | Interface: Amigable
Características:
- Dashboard visual simple
- Control con un clic
- Logs en tiempo real
- Sin tecnicismos
"""

import os
import sys
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
import webbrowser
from linkedin_bot import LinkedInBot

# =============== CONFIGURACIÓN FLASK ===============
app = Flask(__name__, 
           static_folder='static',
           template_folder='templates')

# Variables globales
bot_instance = None
bot_thread = None
is_running = False
current_status = "Listo para comenzar"
last_logs = []
connected_today = 0

# =============== RUTAS PRINCIPALES ===============
@app.route('/')
def home():
    """Página principal del dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Obtiene el estado actual del bot"""
    global current_status, connected_today, last_logs
    
    # Leer estadísticas actuales si existen
    stats_file = Path('logs/session_stats.json')
    stats = {}
    if stats_file.exists():
        try:
            with open(stats_file, 'r') as f:
                data = json.load(f)
                stats = data.get('stats', {})
        except:
            pass
    
    return jsonify({
        'status': current_status,
        'running': is_running,
        'connected_today': stats.get('connections_today', 0),
        'messages_today': stats.get('messages_today', 0),
        'errors_today': stats.get('errors_today', 0),
        'last_logs': last_logs[-10:],  # Últimos 10 logs
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Inicia el bot en un hilo separado"""
    global bot_instance, bot_thread, is_running, current_status
    
    if is_running:
        return jsonify({'success': False, 'message': 'El bot ya está en ejecución'})
    
    # Obtener parámetros del formulario
    data = request.json
    action = data.get('action', 'connect')
    
    # Iniciar en hilo separado
    def run_bot():
        global bot_instance, is_running, current_status, last_logs
        
        try:
            bot_instance = LinkedInBot()
            
            # Inicializar
            current_status = "Inicializando bot..."
            last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando bot")
            
            if not bot_instance.initialize():
                current_status = "Error al inicializar"
                is_running = False
                return
            
            # Login
            current_status = "Iniciando sesión en LinkedIn..."
            last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando sesión")
            
            if not bot_instance.login():
                current_status = "Error en login"
                is_running = False
                return
            
            # Buscar perfiles
            current_status = "Buscando perfiles..."
            last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Buscando perfiles")
            
            profiles = bot_instance.search_profiles()
            
            if not profiles:
                current_status = "No se encontraron perfiles"
                last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] No hay perfiles disponibles")
                is_running = False
                return
            
            # Conectar según acción
            if action == 'connect':
                current_status = f"Conectando con {len(profiles)} perfiles..."
                last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Conectando con {len(profiles)} perfiles")
                
                connected = 0
                for profile in profiles:
                    if not is_running:
                        break
                    
                    if bot_instance.send_connection_request(profile):
                        connected += 1
                        current_status = f"Conectados: {connected}/{len(profiles)}"
                    
                    # Pequeña pausa entre conexiones
                    time.sleep(2)
                
                last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {connected} conexiones exitosas")
            
            # Exportar siempre
            export_path = bot_instance.export_profiles(profiles)
            if export_path:
                last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Exportado a: {export_path}")
            
            # Finalizar
            current_status = "Proceso completado"
            last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Proceso completado exitosamente")
            
        except Exception as e:
            current_status = f"Error: {str(e)}"
            last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {str(e)}")
        
        finally:
            is_running = False
            if bot_instance:
                bot_instance.safe_shutdown()
    
    # Iniciar hilo
    is_running = True
    current_status = "Comenzando..."
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    return jsonify({
        'success': True, 
        'message': 'Bot iniciado correctamente'
    })

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Detiene el bot de forma segura"""
    global is_running, current_status
    
    if not is_running:
        return jsonify({'success': False, 'message': 'El bot no está en ejecución'})
    
    is_running = False
    current_status = "Deteniendo..."
    last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Detenido por usuario")
    
    return jsonify({
        'success': True, 
        'message': 'Deteniendo bot...'
    })

@app.route('/api/config')
def get_config():
    """Obtiene la configuración actual"""
    config_path = Path('config.yaml')
    if config_path.exists():
        return send_file(config_path, as_attachment=False)
    
    return jsonify({'error': 'Configuración no encontrada'})

@app.route('/api/export')
def get_exports():
    """Lista los archivos exportados disponibles"""
    exports_dir = Path('exports')
    if not exports_dir.exists():
        return jsonify({'files': []})
    
    files = []
    for file in exports_dir.glob('*.csv'):
        files.append({
            'name': file.name,
            'size': f"{file.stat().st_size / 1024:.1f} KB",
            'date': datetime.fromtimestamp(file.stat().st_mtime).strftime("%d/%m/%Y %H:%M"),
            'path': str(file)
        })
    
    return jsonify({'files': files})

@app.route('/api/download/<filename>')
def download_file(filename):
    """Descarga un archivo exportado"""
    file_path = Path('exports') / filename
    
    if file_path.exists() and file_path.is_file():
        return send_file(file_path, as_attachment=True)
    
    return jsonify({'error': 'Archivo no encontrado'}), 404

@app.route('/api/logs')
def get_logs():
    """Obtiene logs del sistema"""
    logs_dir = Path('logs')
    logs_content = []
    
    if logs_dir.exists():
        for log_file in logs_dir.glob('*.log'):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logs_content.append({
                        'file': log_file.name,
                        'content': content[-5000:]  # Últimos 5000 caracteres
                    })
            except:
                pass
    
    return jsonify({'logs': logs_content})

@app.route('/api/test')
def test_connection():
    """Prueba la conexión con LinkedIn sin hacer acciones"""
    global current_status, last_logs
    
    current_status = "Probando conexión..."
    last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando prueba de conexión")
    
    try:
        test_bot = LinkedInBot()
        
        # Solo inicializar y login
        if test_bot.initialize():
            if test_bot.login():
                test_bot.safe_shutdown()
                message = "✅ Prueba exitosa: Conexión establecida con LinkedIn"
                current_status = message
                last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
                return jsonify({'success': True, 'message': message})
        
        message = "❌ Prueba fallida: Verifica credenciales"
        current_status = message
        last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        return jsonify({'success': False, 'message': message})
        
    except Exception as e:
        message = f"❌ Error en prueba: {str(e)}"
        current_status = message
        last_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        return jsonify({'success': False, 'message': message})

# =============== FUNCIONES DE UTILIDAD ===============
def create_folders():
    """Crea las carpetas necesarias para el sistema"""
    folders = ['static', 'templates', 'exports', 'logs', 'session', 'backups']
    
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
    
    print("✅ Carpetas creadas correctamente")

def create_default_html():
    """Crea el HTML por defecto si no existe"""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    index_file = templates_dir / 'index.html'
    
    if not index_file.exists():
        html_content = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Assistant - Modo Seguro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #0077b5, #00a0dc);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .header h1 i {
            font-size: 1.5em;
        }
        
        .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .panel {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            border: 2px solid #e9ecef;
        }
        
        .panel h2 {
            color: #0077b5;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #00a0dc;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .panel h2 i {
            font-size: 1.3em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border-left: 5px solid #0077b5;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #0077b5;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .controls {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .btn {
            padding: 18px 25px;
            border: none;
            border-radius: 12px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        
        .btn i {
            font-size: 1.3em;
        }
        
        .btn-primary {
            background: linear-gradient(90deg, #0077b5, #00a0dc);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,119,181,0.3);
        }
        
        .btn-success {
            background: linear-gradient(90deg, #28a745, #20c997);
            color: white;
        }
        
        .btn-success:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(40,167,69,0.3);
        }
        
        .btn-danger {
            background: linear-gradient(90deg, #dc3545, #fd7e14);
            color: white;
        }
        
        .btn-danger:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(220,53,69,0.3);
        }
        
        .btn-secondary {
            background: linear-gradient(90deg, #6c757d, #495057);
            color: white;
        }
        
        .btn-secondary:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(108,117,125,0.3);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
            box-shadow: none !important;
        }
        
        .status-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-top: 20px;
            border: 2px solid;
            transition: all 0.3s;
        }
        
        .status-idle {
            border-color: #6c757d;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        }
        
        .status-running {
            border-color: #28a745;
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            animation: pulse 2s infinite;
        }
        
        .status-error {
            border-color: #dc3545;
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(40,167,69,0.4); }
            70% { box-shadow: 0 0 0 10px rgba(40,167,69,0); }
            100% { box-shadow: 0 0 0 0 rgba(40,167,69,0); }
        }
        
        .status-text {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-time {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .logs-container {
            max-height: 400px;
            overflow-y: auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid #dee2e6;
        }
        
        .log-entry {
            padding: 12px 15px;
            margin-bottom: 8px;
            border-left: 4px solid #0077b5;
            background: #f8f9fa;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            word-break: break-word;
        }
        
        .log-success {
            border-left-color: #28a745;
            background: #d4edda;
        }
        
        .log-error {
            border-left-color: #dc3545;
            background: #f8d7da;
        }
        
        .log-warning {
            border-left-color: #ffc107;
            background: #fff3cd;
        }
        
        .exports-list {
            list-style: none;
            margin-top: 15px;
        }
        
        .export-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: white;
            margin-bottom: 10px;
            border-radius: 10px;
            border: 1px solid #dee2e6;
            transition: all 0.3s;
        }
        
        .export-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .export-info {
            flex: 1;
        }
        
        .export-name {
            font-weight: 600;
            color: #0077b5;
        }
        
        .export-meta {
            font-size: 0.85em;
            color: #6c757d;
            margin-top: 5px;
        }
        
        .export-download {
            padding: 8px 15px;
            background: #0077b5;
            color: white;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.9em;
            transition: all 0.3s;
        }
        
        .export-download:hover {
            background: #005582;
            transform: scale(1.05);
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #0077b5;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .icon {
            display: inline-block;
            width: 24px;
            height: 24px;
            background-size: contain;
            background-repeat: no-repeat;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #dee2e6;
            margin-top: 30px;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-robot"></i> LinkedIn Assistant</h1>
            <p class="subtitle">Versión Segura • Sin Riesgo de Baneo • Interfaz Sencilla</p>
        </div>
        
        <div class="main-content">
            <!-- Panel Izquierdo: Control y Estado -->
            <div class="panel">
                <h2><i class="fas fa-sliders-h"></i> Control del Bot</h2>
                
                <div class="controls">
                    <button class="btn btn-primary" onclick="startBot('connect')" id="btnStart">
                        <i class="fas fa-play"></i> Iniciar Conexiones
                    </button>
                    
                    <button class="btn btn-success" onclick="startBot('search')" id="btnSearch">
                        <i class="fas fa-search"></i> Solo Buscar Perfiles
                    </button>
                    
                    <button class="btn btn-danger" onclick="stopBot()" id="btnStop" disabled>
                        <i class="fas fa-stop"></i> Detener
                    </button>
                    
                    <button class="btn btn-secondary" onclick="testConnection()">
                        <i class="fas fa-wifi"></i> Probar Conexión
                    </button>
                </div>
                
                <div id="statusDisplay" class="status-card status-idle">
                    <div class="status-text">
                        <i class="fas fa-check-circle"></i>
                        <span id="statusText">Listo para comenzar</span>
                    </div>
                    <div class="status-time">
                        Última actualización: <span id="statusTime">--:--:--</span>
                    </div>
                </div>
                
                <div id="alert" class="alert" style="display: none;"></div>
            </div>
            
            <!-- Panel Derecho: Estadísticas -->
            <div class="panel">
                <h2><i class="fas fa-chart-bar"></i> Estadísticas Hoy</h2>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="statConnections">0</div>
                        <div class="stat-label">Conexiones</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value" id="statMessages">0</div>
                        <div class="stat-label">Mensajes</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value" id="statProfiles">0</div>
                        <div class="stat-label">Perfiles Vistos</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value" id="statErrors">0</div>
                        <div class="stat-label">Errores</div>
                    </div>
                </div>
                
                <h2 style="margin-top: 30px;"><i class="fas fa-file-export"></i> Exportaciones</h2>
                <div id="exportsList">
                    <p>Cargando exportaciones...</p>
                </div>
            </div>
            
            <!-- Panel Inferior: Logs -->
            <div class="panel" style="grid-column: span 2;">
                <h2><i class="fas fa-clipboard-list"></i> Registro de Actividad</h2>
                <div class="logs-container" id="logsContainer">
                    <div class="log-entry">Sistema iniciado. Esperando instrucciones...</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><i class="fas fa-shield-alt"></i> Modo Seguro Activado • Límites: 25 conexiones/día • Versión 1.0</p>
            <p>⚠️ No cierres esta ventana mientras el bot esté ejecutándose</p>
        </div>
    </div>
    
    <script>
        let refreshInterval;
        
        // Actualizar estado automáticamente
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Actualizar estadísticas
                    document.getElementById('statConnections').textContent = data.connected_today;
                    document.getElementById('statMessages').textContent = data.messages_today;
                    document.getElementById('statProfiles').textContent = data.profiles_viewed || 0;
                    document.getElementById('statErrors').textContent = data.errors_today;
                    
                    // Actualizar estado
                    document.getElementById('statusText').textContent = data.status;
                    document.getElementById('statusTime').textContent = data.timestamp;
                    
                    // Actualizar botones
                    const btnStart = document.getElementById('btnStart');
                    const btnSearch = document.getElementById('btnSearch');
                    const btnStop = document.getElementById('btnStop');
                    
                    if (data.running) {
                        btnStart.disabled = true;
                        btnSearch.disabled = true;
                        btnStop.disabled = false;
                        
                        // Cambiar estilo de estado
                        const statusDiv = document.getElementById('statusDisplay');
                        statusDiv.className = 'status-card status-running';
                        statusDiv.querySelector('.status-text i').className = 'fas fa-sync-alt fa-spin';
                    } else {
                        btnStart.disabled = false;
                        btnSearch.disabled = false;
                        btnStop.disabled = true;
                        
                        const statusDiv = document.getElementById('statusDisplay');
                        statusDiv.className = 'status-card status-idle';
                        statusDiv.querySelector('.status-text i').className = 'fas fa-check-circle';
                    }
                    
                    // Actualizar logs
                    updateLogs(data.last_logs);
                })
                .catch(error => {
                    console.error('Error actualizando estado:', error);
                });
        }
        
        // Actualizar logs
        function updateLogs(logs) {
            const container = document.getElementById('logsContainer');
            if (!logs || logs.length === 0) return;
            
            // Solo actualizar si hay nuevos logs
            const currentLogs = container.querySelectorAll('.log-entry');
            if (currentLogs.length === logs.length) return;
            
            container.innerHTML = '';
            logs.forEach(log => {
                const logDiv = document.createElement('div');
                logDiv.className = 'log-entry';
                
                // Color según tipo de log
                if (log.includes('ERROR') || log.includes('Error')) {
                    logDiv.classList.add('log-error');
                } else if (log.includes('✅') || log.includes('éxito') || log.includes('exitosamente')) {
                    logDiv.classList.add('log-success');
                } else if (log.includes('⚠️') || log.includes('Advertencia') || log.includes('alerta')) {
                    logDiv.classList.add('log-warning');
                }
                
                logDiv.textContent = log;
                container.appendChild(logDiv);
            });
            
            // Scroll al final
            container.scrollTop = container.scrollHeight;
        }
        
        // Cargar exportaciones
        function loadExports() {
            fetch('/api/export')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('exportsList');
                    
                    if (!data.files || data.files.length === 0) {
                        container.innerHTML = '<p>No hay exportaciones todavía.</p>';
                        return;
                    }
                    
                    let html = '<ul class="exports-list">';
                    data.files.forEach(file => {
                        html += `
                            <li class="export-item">
                                <div class="export-info">
                                    <div class="export-name">${file.name}</div>
                                    <div class="export-meta">
                                        ${file.size} • ${file.date}
                                    </div>
                                </div>
                                <a href="/api/download/${file.name}" class="export-download">
                                    <i class="fas fa-download"></i> Descargar
                                </a>
                            </li>
                        `;
                    });
                    html += '</ul>';
                    
                    container.innerHTML = html;
                });
        }
        
        // Iniciar bot
        function startBot(action) {
            const alertDiv = document.getElementById('alert');
            alertDiv.style.display = 'none';
            
            const actionName = action === 'connect' ? 'conexiones' : 'búsqueda';
            
            if (!confirm(`¿Iniciar ${actionName}? El bot trabajará de forma segura.`)) {
                return;
            }
            
            fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action: action })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('✅ Bot iniciado correctamente. Revisa los logs para el progreso.', 'success');
                } else {
                    showAlert('❌ ' + data.message, 'danger');
                }
            })
            .catch(error => {
                showAlert('❌ Error al iniciar el bot: ' + error, 'danger');
            });
        }
        
        // Detener bot
        function stopBot() {
            if (!confirm('¿Detener el bot? Se cerrará de forma segura.')) {
                return;
            }
            
            fetch('/api/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('⏸️ Bot detenido correctamente.', 'success');
                }
            });
        }
        
        // Probar conexión
        function testConnection() {
            const alertDiv = document.getElementById('alert');
            alertDiv.innerHTML = '<div class="loading"></div> Probando conexión con LinkedIn...';
            alertDiv.className = 'alert alert-warning';
            alertDiv.style.display = 'block';
            
            fetch('/api/test')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alertDiv.innerHTML = data.message;
                        alertDiv.className = 'alert alert-success';
                    } else {
                        alertDiv.innerHTML = data.message;
                        alertDiv.className = 'alert alert-danger';
                    }
                    alertDiv.style.display = 'block';
                })
                .catch(error => {
                    alertDiv.innerHTML = '❌ Error en la prueba: ' + error;
                    alertDiv.className = 'alert alert-danger';
                    alertDiv.style.display = 'block';
                });
        }
        
        // Mostrar alerta
        function showAlert(message, type) {
            const alertDiv = document.getElementById('alert');
            alertDiv.textContent = message;
            alertDiv.className = `alert alert-${type}`;
            alertDiv.style.display = 'block';
            
            // Ocultar después de 5 segundos
            setTimeout(() => {
                alertDiv.style.display = 'none';
            }, 5000);
        }
        
        // Inicializar
        document.addEventListener('DOMContentLoaded', function() {
            // Iniciar actualización automática
            updateStatus();
            loadExports();
            
            refreshInterval = setInterval(() => {
                updateStatus();
                // Actualizar exportaciones cada 30 segundos
                if (Math.floor(Date.now() / 1000) % 30 === 0) {
                    loadExports();
                }
            }, 2000);
            
            // Cargar exportaciones cada 30 segundos
            setInterval(loadExports, 30000);
            
            // Confirmar antes de cerrar si el bot está ejecutándose
            window.addEventListener('beforeunload', function(e) {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        if (data.running) {
                            e.preventDefault();
                            e.returnValue = 'El bot está en ejecución. ¿Estás seguro de querer salir?';
                        }
                    });
            });
        });
        
        // Limpiar intervalo al salir
        window.addEventListener('unload', function() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        });
    </script>
</body>
</html>'''
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ HTML template creado correctamente")

# =============== EJECUCIÓN PRINCIPAL ===============
if __name__ == "__main__":
    print("=" * 60)
    print("🌐 INICIANDO INTERFAZ WEB DE LINKEDIN BOT")
    print("=" * 60)
    
    # Crear estructura de carpetas
    create_folders()
    create_default_html()
    
    # Verificar que existe config.yaml
    config_path = Path('config.yaml')
    if not config_path.exists():
        print("❌ ERROR: No se encontró config.yaml")
        print("💡 Crea el archivo config.yaml con tus credenciales")
        sys.exit(1)
    
    # Abrir navegador automáticamente
    port = 5000
    url = f"http://localhost:{port}"
    
    print(f"\n✅ Sistema listo")
    print(f"📁 Carpetas creadas: static/, templates/, exports/, logs/, session/, backups/")
    print(f"🌐 La interfaz web se abrirá automáticamente en tu navegador")
    print(f"🔗 Si no se abre, visita manualmente: {url}")
    print(f"🛑 Para detener el servidor, presiona Ctrl+C")
    print("\n" + "=" * 60)
    
    # Abrir navegador después de 2 segundos
    threading.Timer(2, lambda: webbrowser.open(url)).start()
    
    # Iniciar servidor Flask
    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
        sys.exit(0)
