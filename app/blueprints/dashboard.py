from flask import Blueprint, render_template, session, jsonify, current_app
from .auth import login_required
from ..db import get_db, get_current_mode
from ..services.remote import RemoteExecutor
import subprocess
import platform

dashboard_bp = Blueprint('dashboard', __name__)

def format_size(size_bytes):
    """Auxiliar para mostrar tamaño de disco"""
    if size_bytes == 0: return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = size_bytes / p
    
    if i == 4: # TB
        val = math.floor(s * 100) / 100
        return f"{val:.2f} TB".replace('.', ',')
    elif i == 3: # GB
        if s < 10:
            val = math.floor(s * 100) / 100
            return f"{val:.2f} GB".replace('.', ',')
        else:
            val = math.floor(s * 10) / 10
            return f"{val:.1f} GB".replace('.', ',')
    else:
        val = math.floor(s * 10) / 10
        return f"{val:g} {size_name[i]}".replace('.', ',')

@dashboard_bp.route('/dashboard')
@login_required
def index():
    db = get_db()
    logs = db.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10").fetchall()
    backup_logs = db.execute("SELECT * FROM audit_logs WHERE action LIKE '%BACKUP%' ORDER BY timestamp DESC LIMIT 10").fetchall()
    
    disks = {} # Se cargan vía API ahora
    global_ip = current_app.config['GLOBAL_SERVER_IP']
    
    # Check Global Server Status (Ping)
    param = '-c' # Linux
    res = subprocess.call(['/usr/bin/ping', param, '1', global_ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    global_status = "ONLINE" if res == 0 else "OFFLINE"

    # ROBOCOPY LOG INFO:
    backup_log = {}
    try:
        user = current_app.config.get('WINDOWS_USER')
        password = current_app.config.get('WINDOWS_PASS')
        executor = RemoteExecutor(global_ip, user=user, password=password)
        log_path = current_app.config['REMOTE_LOG_PATH']
        # Leemos las ultimas 5000 lineas para asegurar capturar el bloque completo incluso en backups grandes
        cmd = f'Get-Content -Path "{log_path}" -Tail 5000 -Encoding UTF8'
        success, content = executor.run_ps_command(cmd)
        if success:
            from ..utils import parse_robocopy_log
            backup_log = parse_robocopy_log(content)
    except Exception as e:
        backup_log = {"status": "ERROR", "msg": str(e)}

    return render_template('index.html', 
                           logs=logs, 
                           backup_logs=backup_logs, 
                           disks=disks, 
                           backup_log=backup_log,
                           user=session.get('username'), 
                           role=session.get('role'), 
                           current_mode=get_current_mode(),
                           global_status=global_status)
@dashboard_bp.route('/api/disks')
@login_required
def api_disks():
    global_ip = current_app.config['GLOBAL_SERVER_IP']
    emergency_ip = current_app.config['EMERGENCY_SERVER_IP']
    disks = {}
    targets = [(global_ip, "Global"), (emergency_ip, "Emerg")]
    
    print(f"DEBUG: api_disks() iniciado")
    win_user = current_app.config.get('WINDOWS_USER')
    win_pass = current_app.config.get('WINDOWS_PASS')
    
    for ip, suffix in targets:
        print(f"DEBUG: Consultando servidor {suffix} ({ip})...")
        try:
            executor = RemoteExecutor(ip, user=win_user, password=win_pass)
            # Consultamos todos los discos configurados
            for d_letter in current_app.config.get('MONITOR_DISKS', ["D:", "E:"]):
                # Comando más preciso (Get-Volume)
                print(f"DEBUG: Consultando disco {d_letter} en {ip}...")
                cmd = f'Get-Volume -DriveLetter {d_letter.replace(":","")} | Select-Object Size, SizeRemaining | ConvertTo-Json'
                success, output = executor.run_ps_command(cmd)
                print(f"DEBUG: Disco {d_letter} en {ip} success={success}")
                # Definir etiqueta base para errores
                label = f"{suffix} ({d_letter})"
                
                if success and output and output.strip().startswith('{'):
                    import json
                    try:
                        data = json.loads(output)
                        total = int(data.get('Size', 0))
                        free = int(data.get('SizeRemaining', 0))
                        
                        if total > 0:
                            used = total - free
                            # Determinar función ARCHIVOS/EDICION según el servidor y la letra
                            if suffix == "Global":
                                func = "ARCHIVOS" if d_letter == "D:" else "EDICION"
                            else:
                                func = "ARCHIVOS" if d_letter == "E:" else "EDICION"
                            label = f"{suffix} - {func} ({d_letter})"
                            disks[label] = {
                                "total": format_size(total),
                                "used": format_size(used),
                                "free": format_size(free),
                                "percent": round((used/total)*100, 1),
                                "func": func,  # Para ordenar en JS
                                "drive": d_letter,
                                "server": suffix,
                                "status": "OK"
                            }
                        else: disks[label] = {"status": "OFFLINE", "server": suffix, "drive": d_letter}
                    except: disks[label] = {"status": "OFFLINE", "server": suffix, "drive": d_letter}
                else:
                    disks[label] = {"status": "OFFLINE", "server": suffix, "drive": d_letter}
        except:
            # Si falla la conexión al servidor completo
            for d in ["D:", "E:"]:
                lbl = f"{suffix} ({d})"
                disks[lbl] = {"status": "OFFLINE", "server": suffix, "drive": d}
    return jsonify(disks)

@dashboard_bp.route('/api/status')
@login_required
def api_status():
    global_ip = current_app.config['GLOBAL_SERVER_IP']
    res = subprocess.call(['/usr/bin/ping', '-c', '1', '-W', '1', global_ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return jsonify({"global": "ONLINE" if res==0 else "OFFLINE", "mode": get_current_mode()})
