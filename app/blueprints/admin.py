from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from .auth import login_required, admin_required
from ..db import get_db, log_audit, set_current_mode
from werkzeug.security import generate_password_hash
from ..services.remote import RemoteExecutor
import json
import base64
import xml.etree.ElementTree as ET
import re
import os

admin_bp = Blueprint('admin', __name__)

# --- UTILS XML ---
def generate_task_xml(rules):
    # Genera XML valido para Task Scheduler v1.2
    # Recibe lista de reglas: [{'time': 'HH:MM', 'days': ['MON', 'TUE'] or []}, ...]
    # Adaptado del original
    BATCH_PATH_REMOTE = current_app.config.get('BATCH_PATH_REMOTE', r"C:\RunBackup.bat")
    
    xml = r"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Date>2024-01-01T00:00:00</Date><Author>SistemaHA</Author></RegistrationInfo>
  <Triggers>"""
    for rule in rules:
        t = rule.get('time', '00:00')
        days = rule.get('days', [])
        start_boundary = f"2024-01-01T{t}:00"
        
        if not days:
            # Diario
            xml += f"""<CalendarTrigger><StartBoundary>{start_boundary}</StartBoundary><Enabled>true</Enabled><ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay></CalendarTrigger>"""
        else:
            # Semanal
            d_map = {"MON":"Monday","TUE":"Tuesday","WED":"Wednesday","THU":"Thursday","FRI":"Friday","SAT":"Saturday","SUN":"Sunday"}
            clean_days = []
            for d in days:
                 if d in d_map: clean_days.append(d_map[d])
                 elif d in d_map.values(): clean_days.append(d)
            
            if not clean_days:
                 xml += f"""<CalendarTrigger><StartBoundary>{start_boundary}</StartBoundary><Enabled>true</Enabled><ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay></CalendarTrigger>"""
            else:
                 days_xml = "".join([f"<{x} />" for x in clean_days])
                 xml += f"""<CalendarTrigger><StartBoundary>{start_boundary}</StartBoundary><Enabled>true</Enabled><ScheduleByWeek><DaysOfWeek>{days_xml}</DaysOfWeek><WeeksInterval>1</WeeksInterval></ScheduleByWeek></CalendarTrigger>"""
    xml += rf"""</Triggers><Principals><Principal id="Author"><UserId>S-1-5-18</UserId><RunLevel>HighestAvailable</RunLevel></Principal></Principals><Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries><AllowHardTerminate>true</AllowHardTerminate><StartWhenAvailable>true</StartWhenAvailable><RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable><IdleSettings><StopOnIdleEnd>true</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings><AllowStartOnDemand>true</AllowStartOnDemand><Enabled>true</Enabled><Hidden>false</Hidden><RunOnlyIfIdle>false</RunOnlyIfIdle><WakeToRun>false</WakeToRun><ExecutionTimeLimit>PT72H</ExecutionTimeLimit><Priority>7</Priority></Settings><Actions Context="Author"><Exec><Command>{BATCH_PATH_REMOTE}</Command></Exec></Actions></Task>"""
    return xml

def parse_remote_xml(xml_string):
    active_days = []
    active_times = []
    groups = {} 
    status_text = ""
    has_daily_gui = False
    debug_log = []
    
    try:
        xml_string = re.sub(r'\sxmlns="[^"]+"', '', xml_string)
        xml_string = re.sub(r'<\w+:', '<', xml_string)
        xml_string = re.sub(r'</\w+:', '</', xml_string)
        root = ET.fromstring(xml_string)
        
        if root.find(".//BootTrigger") is not None: status_text = "Modo: Al Inicio del Sistema"
        
        triggers = root.findall(".//CalendarTrigger")
        debug_log.append(f"Triggers encontrados: {len(triggers)}")
        
        for i, trigger in enumerate(triggers):
            t_str = "Unknown"
            sb = trigger.find(".//StartBoundary") 
            if sb is None: sb = trigger.find("StartBoundary")
            if sb is not None and sb.text:
                match = re.search(r'T(\d{1,2}):(\d{2})', sb.text)
                if match: t_str = f"{match.group(1).zfill(2)}:{match.group(2)}"
            
            has_day = trigger.find(".//ScheduleByDay") is not None
            has_week = trigger.find(".//ScheduleByWeek") is not None
            
            days_key = "UNKNOWN"
            days_label = "Desconocido"
            days_codes_list = []
            
            if has_day:
                days_key = "DAILY"
                days_label = "TODOS LOS DÍAS"
                debug_log.append(f"T{i+1}({t_str}): DAILY")
            elif has_week:
                week_node = trigger.find(".//ScheduleByWeek/DaysOfWeek")
                if week_node is not None:
                    d_map = {"Monday":"Lun","Tuesday":"Mar","Wednesday":"Mié","Thursday":"Jue","Friday":"Vie","Saturday":"Sáb","Sunday":"Dom"}
                    d_codes_map = {"Monday":"MON","Tuesday":"TUE","Wednesday":"WED","Thursday":"THU","Friday":"FRI","Saturday":"SAT","Sunday":"SUN"}
                    found_days = []
                    found_codes = []
                    for child in week_node:
                        if child.tag in d_map:
                            found_days.append(d_map[child.tag])
                            if child.tag in d_codes_map:
                                found_codes.append(d_codes_map[child.tag])
                    if found_days:
                        found_codes.sort()
                        days_key = ",".join(found_codes)
                        days_label = ", ".join(found_days)
                        days_codes_list = found_codes
            
            if days_key not in groups: 
                groups[days_key] = {'label': days_label, 'times': [], 'codes': days_codes_list}
            if t_str not in groups[days_key]['times']: groups[days_key]['times'].append(t_str)
            if t_str not in active_times: active_times.append(t_str)
            if days_key == "DAILY": has_daily_gui = True
            
        if not status_text: 
            status_text = f"Detalle: {'; '.join(debug_log)}"
        if has_daily_gui: active_days = [] 
    except Exception as e: status_text = f"Error: {str(e)}"
        
    summary_list = []
    for k, v in groups.items():
        v['times'].sort()
        summary_list.append(v)
    summary_list.sort(key=lambda x: 0 if "TODOS" in x['label'] else 1)
    return active_days, active_times, status_text, summary_list


# --- FAILOVER METHODS ---
def execute_failover_logic(u="SYSTEM"):
    try:
        log_audit("EMERGENCIA_ACTIVANDO", "Iniciando secuencia de Emergencia...", "ALERTA", u)
        executor = RemoteExecutor(current_app.config['EMERGENCY_SERVER_IP'])
        # Asumimos que el script existe en el remoto
        ps_command = fr'& "{current_app.config["REMOTE_SCRIPTS_DIR"]}\trigger_failover.ps1"'
        success, output = executor.run_ps_command(ps_command)
        if success:
            set_current_mode("READ_WRITE")
            log_audit("EMERGENCIA_ACTIVA", "Escritura Habilitada en Emergencia.", "SUCCESS", u)
            return True, output
        else:
            log_audit("FAILOVER_FAIL", f"Error Remoto: {output}", "ERROR", u)
            return False, output
    except Exception as e: return False, str(e)

def execute_failback_logic(u="SYSTEM"):
    try:
        log_audit("EMERGENCIA_DESACTIVANDO", "Iniciando Restauracion...", "INFO", u)
        executor = RemoteExecutor(current_app.config['EMERGENCY_SERVER_IP'])
        ps_command = fr'& "{current_app.config["REMOTE_SCRIPTS_DIR"]}\trigger_failback.ps1"'
        success, output = executor.run_ps_command(ps_command)
        if success:
            set_current_mode("READ_ONLY")
            log_audit("EMERGENCIA_INACTIVA", "Datos restaurados a Global.", "SUCCESS", u)
            return True, output
        else:
            log_audit("FAILBACK_FAIL", f"Error Remoto: {output}", "ERROR", u)
            return False, output
    except Exception as e: return False, str(e)

@admin_bp.route('/api/action', methods=['POST'])
@login_required
def action():
    data = request.json
    action_type = data.get('action')
    if action_type == 'failover':
        success, output = execute_failover_logic(session['username'])
    else:
        success, output = execute_failback_logic(session['username'])
    return jsonify({"status": "SUCCESS" if success else "ERROR", "output": output})

# --- USER MANAGEMENT ---
@admin_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = get_db().execute("SELECT * FROM users").fetchall()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/admin/users', methods=['POST'])
@login_required
def create_user(): 
    if session.get('role') != 'admin': return redirect(url_for('dashboard.index'))
    u, p = request.form.get('new_username'), request.form.get('new_password')
    if u and p:
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (u, generate_password_hash(p), "operator"))
            db.commit()
            flash("Usuario creado", "success")
        except: flash("Error creando usuario", "error")
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if session.get('role') != 'admin': return redirect(url_for('dashboard.index'))
    if user_id != session['user_id']: 
        db = get_db()
        db.execute("DELETE FROM users WHERE id=?", (user_id,))
        db.commit()
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/users/change_password/<int:user_id>', methods=['POST'])
@login_required
def change_user_password(user_id):
    if session.get('role') != 'admin': 
        flash("Acceso denegado", "error")
        return redirect(url_for('dashboard.index'))
    
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not new_password or not confirm_password:
        flash("Ambos campos son requeridos", "error")
        return redirect(url_for('admin.manage_users'))
    
    if new_password != confirm_password:
        flash("Las contraseñas no coinciden", "error")
        return redirect(url_for('admin.manage_users'))
    
    if len(new_password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres", "error")
        return redirect(url_for('admin.manage_users'))
    
    try:
        db = get_db()
        db.execute("UPDATE users SET password=? WHERE id=?", (generate_password_hash(new_password), user_id))
        db.commit()
        flash("Contraseña actualizada exitosamente", "success")
    except Exception as e:
        flash(f"Error al cambiar contraseña: {e}", "error")
    
    return redirect(url_for('admin.manage_users'))

# --- SCHEDULE & BACKUP ---
@admin_bp.route('/admin/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if session.get('role') != 'admin': return redirect(url_for('dashboard.index'))
    
    loaded_days = []
    loaded_times = []
    config_loaded = False
    current_status_msg = ""
    summary_list = []
    
    global_ip = current_app.config['GLOBAL_SERVER_IP']
    task_name = current_app.config.get('REMOTE_TASK_NAME', "SistemaHA_Backup_Robocopy")
    
    if request.method == 'POST':
        if 'load_config' in request.form:
            # LEER XML REMOTO usando WinRM
            try:
                executor = RemoteExecutor(global_ip)
                # Exportar tarea a XML temporal, leer contenido, borrar
                ps_script = f"""
                schtasks /Query /TN "{task_name}" /XML
                """
                # La salida de Query /XML es el XML directo en stdout
                success, output = executor.run_ps_command(ps_script)
                
                if success and "<Task" in output:
                    # Parsear
                    loaded_days, loaded_times, current_status_msg, summary_list = parse_remote_xml(output)
                    config_loaded = True
                    flash(f"Lectura Exitosa.", "success")
                else:
                    flash(f"No se pudo leer la tarea. ¿Existe? Error: {output[:100]}", "warning")
            except Exception as e:
                flash(f"Error leyendo config remota: {e}", "error")
        
        elif 'save_config' in request.form:
            config_json = request.form.get('schedule_config')
            if config_json is not None:
                try:
                    rules = json.loads(config_json)
                    xml_content = generate_task_xml(rules)
                    
                    # GUARDAR XML TEMPORALMENTE EN EL UBUNTU
                    # Para que el Windows lo descargue
                    temp_xml_path = os.path.join(current_app.root_path, 'static', 'pending_task.xml')
                    with open(temp_xml_path, 'w', encoding='utf-16') as f:
                        f.write(xml_content)
                    
                    # COMANDO REMOTO CORTO: Descargar y Aplicar
                    panel_ip = current_app.config['PANEL_IP']
                    # Usamos -UseBasicParsing para evitar problemas con IE
                    ps_script = f"""
                    $url = "http://{panel_ip}:5001/static/pending_task.xml"
                    Invoke-WebRequest -Uri $url -OutFile "C:\\Windows\\Temp\\ha_task_import.xml" -UseBasicParsing
                    schtasks /Create /XML "C:\\Windows\\Temp\\ha_task_import.xml" /TN "{task_name}" /F
                    """
                    
                    executor = RemoteExecutor(global_ip)
                    success, output = executor.run_ps_command(ps_script)
                    
                    if success:
                         flash(f"¡Configuración Aplicada! ({len(rules)} reglas).", "success")
                         config_loaded = True
                    else:
                         flash(f"Error al guardar: {output}", "error")
                         
                except Exception as e: flash(f"Excepción General: {str(e)}", "error")

    hours_grid = []
    for h in range(24):
        for m in [0, 30]: hours_grid.append(f"{h:02d}:{m:02d}")
    return render_template('schedule.html', hours=hours_grid, loaded_days=loaded_days, loaded_times=loaded_times, config_loaded=config_loaded, current_status=current_status_msg, summary_list=summary_list)

@admin_bp.route('/admin/run_backup', methods=['POST'])
@login_required
@admin_required
def run_backup():
    if 'run_now' in request.form:
        global_ip = current_app.config['GLOBAL_SERVER_IP']
        task_name = current_app.config.get('REMOTE_TASK_NAME', "SistemaHA_Backup_Robocopy")
        
        executor = RemoteExecutor(global_ip)
        cmd = f'schtasks /Run /TN "{task_name}"'
        success, output = executor.run_ps_command(cmd)
        
        if success:
            flash("¡Tarea de Backup INICIADA con éxito!", "success")
        else:
            flash(f"Error al iniciar tarea: {output}", "error")
            
    return redirect(url_for('dashboard.index'))
