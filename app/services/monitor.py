import threading
import time
import subprocess
import platform
from flask import current_app
from ..db import get_db, log_audit, get_current_mode, set_current_mode
from .remote import RemoteExecutor

class HAMonitor(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.daemon = True
        self.last_status = "UNKNOWN"
        self.consecutive_fails = 0
        self.is_running = True

    def run(self):
        with self.app.app_context():
            print(">>> INICIANDO MONITOR DE ALTA DISPONIBILIDAD...")
            log_audit("MONITOR_START", "Servicio de monitoreo iniciado", "INFO")
            
            while self.is_running:
                try:
                    global_ip = current_app.config['GLOBAL_SERVER_IP']
                    current_mode = get_current_mode()
                    
                    # PING
                    param = '-c' # Linux
                    res = subprocess.call(['/usr/bin/ping', param, '1', '-W', '2', global_ip], 
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    is_online = (res == 0)
                    
                    if is_online:
                        self.consecutive_fails = 0
                        status = "ONLINE"
                    else:
                        self.consecutive_fails += 1
                        status = "OFFLINE" if self.consecutive_fails >= 10 else self.last_status

                    # LOGICA DE TRANSICION
                    if status != self.last_status and self.last_status != "UNKNOWN":
                        log_audit("ESTADO_RED", f"Server Global ahora está {status}", "ALERTA" if status=="OFFLINE" else "INFO")
                        
                        # --- CASO: CAÍDA (OFFLINE) ---
                        if status == "OFFLINE" and current_mode == "READ_ONLY":
                            self.trigger_automatic_failover()
                        
                        # --- CASO: RECUPERACIÓN (ONLINE) ---
                        elif status == "ONLINE" and current_mode == "READ_WRITE":
                            # Esperar un poco para estabilidad
                            time.sleep(30)
                            self.trigger_automatic_failback()
                    
                    self.last_status = status
                    
                except Exception as e:
                    print(f"Error en monitor: {e}")
                
                time.sleep(3)

    def trigger_automatic_failover(self):
        """Activa el modo Emergencia automáticamente"""
        from ..blueprints.admin import execute_failover_logic
        log_audit("AUTO_FAILOVER", "Iniciando Failover automático por caída de red", "ALERTA", "SYSTEM")
        success, output = execute_failover_logic("AUTO_BOT")
        if success:
            log_audit("AUTO_FAILOVER_OK", "Modo Emergencia activado exitosamente", "SUCCESS", "SYSTEM")
        else:
            log_audit("AUTO_FAILOVER_ERR", f"Error en Failover automático: {output}", "ERROR", "SYSTEM")

    def trigger_automatic_failback(self):
        """Restaura el modo normal automáticamente con sincronización inversa"""
        from ..blueprints.admin import execute_failback_logic
        global_ip = current_app.config['GLOBAL_SERVER_IP']
        task_name = current_app.config.get('REMOTE_TASK_NAME', "SistemaHA_Backup_Robocopy")
        
        log_audit("AUTO_FAILBACK", "Iniciando recuperación automática del sistema", "INFO", "SYSTEM")
        
        # 1. SEGURIDAD: Deshabilitar tarea de backup en Global ANTES de sincronizar
        try:
            executor = RemoteExecutor(global_ip)
            executor.run_ps_command(f'schtasks /Change /TN "{task_name}" /Disable')
            log_audit("AUTO_FAILBACK_SEC", "Tarea de backup deshabilitada en Global por seguridad", "INFO", "SYSTEM")
        except: pass

        # 2. Ejecutar Failback (Bloquea escritura en Emergencia + Sincro Inversa)
        success, output = execute_failback_logic("AUTO_BOT")
        
        if success:
            # 3. Rehabilitar tarea de backup en Global
            try:
                executor.run_ps_command(f'schtasks /Change /TN "{task_name}" /Enable')
                log_audit("AUTO_FAILBACK_OK", "Sistema restaurado y backups rehabilitados", "SUCCESS", "SYSTEM")
            except: pass
        else:
            log_audit("AUTO_FAILBACK_ERR", f"Error en restauración automática: {output}", "ERROR", "SYSTEM")

def start_monitor(app):
    monitor = HAMonitor(app)
    monitor.start()
    return monitor
