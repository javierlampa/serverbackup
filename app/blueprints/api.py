from flask import Blueprint, jsonify, request, make_response, current_app
from .auth import login_required
from ..db import log_audit
from ..services.remote import RemoteExecutor
import os
import time
import json

api_bp = Blueprint('api', __name__)

# Cache para deltas de red: { (ip, adapter_name): (timestamp, sent_bytes, recv_bytes) }
network_stats_cache = {}

@api_bp.route('/api/view_log', methods=['GET'])
@login_required
def api_view_log():
    try:
        executor = RemoteExecutor(current_app.config['GLOBAL_SERVER_IP'])
        log_path = current_app.config['REMOTE_LOG_PATH']
        # Leemos las ultimas 1000 lineas usando PowerShell
        cmd = f'Get-Content -Path "{log_path}" -Tail 1000 -Encoding UTF8'
        success, content = executor.run_ps_command(cmd)
        
        if success:
            return jsonify({"status": "ok", "content": content})
        else:
            return jsonify({"status": "error", "content": "Error leyendo log remoto: " + content}), 500
    except Exception as e:
        return jsonify({"status": "error", "content": str(e)}), 500

@api_bp.route('/api/download_log', methods=['GET'])
@login_required
def api_download_log():
    try:
        executor = RemoteExecutor(current_app.config['GLOBAL_SERVER_IP'])
        log_path = current_app.config['REMOTE_LOG_PATH']
        # Leemos el log para descarga (limitado a ultimas 5000 lineas por performance)
        cmd = f'Get-Content -Path "{log_path}" -Tail 5000 -Encoding UTF8'
        success, content = executor.run_ps_command(cmd)
        
        if success:
            response = make_response(content)
            response.headers["Content-Disposition"] = "attachment; filename=robocopy_log_recent.txt"
            response.headers["Content-type"] = "text/plain; charset=utf-8"
            return response
        else:
            return "Error recuperando log para descarga: " + content, 500
    except Exception as e:
        return str(e), 500

@api_bp.route('/api/backup_event', methods=['POST'])
def api_backup_event():
    """Endpoint para recibir eventos de backup desde SERVERGLOBAL"""
    # Autenticación con token simple
    auth_token = request.headers.get('X-Auth-Token')
    if auth_token != 'BACKUP_SECRET_TOKEN_2024':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    action = data.get('action')
    details = data.get('details', '')
    
    if action not in ['BACKUP_START', 'BACKUP_END']:
        return jsonify({"error": "Invalid action"}), 400
    
    # Usar el resultado enviado o inferir uno por defecto
    result = data.get('result')
    if not result:
        result = 'INFO' if action == 'BACKUP_START' else 'SUCCESS'
    
    # REGISTRAR EVENTO
    log_audit(action, details, result, u="SERVERGLOBAL")
    
    return jsonify({"status": "OK", "message": "Event logged"})
        
@api_bp.route('/api/network', methods=['GET'])
@login_required
def api_network():
    """Retorna estadísticas de red de ambos servidores en paralelo"""
    from threading import Thread
    results = {}
    servers = {
        'global': current_app.config['GLOBAL_SERVER_IP'],
        'emergency': current_app.config['EMERGENCY_SERVER_IP']
    }
    
    # Extraer credenciales para pasarlas a los hilos sin depender del contexto
    win_user = current_app.config.get('WINDOWS_USER')
    win_pass = current_app.config.get('WINDOWS_PASS')
    
    threads = []
    now = time.time()

    def fetch_stats(srv_name, ip):
        try:
            # Pasamos las credenciales explícitamente para evitar problemas de contexto en hilos
            executor = RemoteExecutor(ip, user=win_user, password=win_pass)
            cmd = 'Get-NetAdapterStatistics | Select-Object Name, ReceivedBytes, SentBytes | ConvertTo-Json'
            success, output = executor.run_ps_command(cmd)
            
            if success and output:
                try:
                    stats_list = json.loads(output)
                    if isinstance(stats_list, dict):
                        stats_list = [stats_list]
                        
                    for adapter in stats_list:
                        name = adapter['Name']
                        recv = adapter['ReceivedBytes']
                        sent = adapter['SentBytes']
                        
                        cache_key = (ip, name)
                        speed_recv, speed_sent = 0, 0
                        
                        if cache_key in network_stats_cache:
                            old_time, old_sent, old_recv = network_stats_cache[cache_key]
                            dt = now - old_time
                            if dt > 0:
                                speed_sent = int(((sent - old_sent) * 8) / dt)
                                speed_recv = int(((recv - old_recv) * 8) / dt)
                                if speed_sent < 0: speed_sent = 0
                                if speed_recv < 0: speed_recv = 0
                        
                        network_stats_cache[cache_key] = (now, sent, recv)
                        results[srv_name].append({
                            "name": name,
                            "sent_bps": speed_sent,
                            "recv_bps": speed_recv,
                            "total_sent": sent,
                            "total_recv": recv
                        })
                except Exception as je:
                    print(f"Error JSON Red ({srv_name}): {je}")
        except Exception as e:
            print(f"Error Conexión Red ({srv_name}): {e}")

    for srv_name, ip in servers.items():
        results[srv_name] = [] # Inicializar antes de los hilos
        t = Thread(target=fetch_stats, args=(srv_name, ip))
        t.start()
        threads.append(t)

    for t in threads:
        t.join(timeout=5)
            
    return jsonify(results)
