import threading
import winrm
from flask import current_app
_local_data = threading.local()

def _get_local_cache():
    if not hasattr(_local_data, 'session_cache'):
        _local_data.session_cache = {}
    return _local_data.session_cache

class RemoteExecutor:
    def __init__(self, target_ip, user=None, password=None):
        self.target_ip = target_ip
        # Si no se pasan credenciales, intentamos obtenerlas del contexto de Flask
        if not user or not password:
            from flask import current_app
            self.user = user or current_app.config.get('WINDOWS_USER', 'Administrador')
            self.password = password or current_app.config.get('WINDOWS_PASS', 'dsP3026x&')
        else:
            self.user = user
            self.password = password

    def _get_session(self):
        """Lazy initialization and caching of WinRM session (Thread-Safe)"""
        cache = _get_local_cache()
        cache_key = (self.target_ip, self.user)
        if cache_key not in cache:
            url = f"http://{self.target_ip}:5985/wsman"
            # Creamos la sesión para este hilo específico
            cache[cache_key] = winrm.Session(url, auth=(self.user, self.password), transport='ntlm')
        return cache[cache_key]

    def run_ps_command(self, ps_script_block):
        """Executes a PowerShell command or script block"""
        try:
            s = self._get_session()
            # Envolvemos el comando en powershell.exe para asegurar contexto
            # O usamos run_ps de la libreria si disponible, pero run_cmd es mas directo
            # Codificar script complejo en Base64 a veces es mejor, pero probemos directo primero
            # Para comandos simples 'run_ps' de winrm suele ser: run_ps(script)
            
            rs = s.run_ps(ps_script_block)
            
            stdout = rs.std_out.decode('utf-8', errors='replace')
            stderr = rs.std_err.decode('utf-8', errors='replace')
            
            if rs.status_code == 0:
                print(f"[{self.target_ip}] SUCCESS")
                return True, stdout
            else:
                print(f"[{self.target_ip}] ERROR: {stderr}")
                return False, stderr + "\n" + stdout
                
        except Exception as e:
            return False, str(e)

    def run_cmd(self, command):
        """Executes a standard CMD command"""
        try:
            s = self._get_session()
            rs = s.run_cmd(command)
            stdout = rs.std_out.decode('cp850', errors='replace') # Windows legacy codepage
            stderr = rs.std_err.decode('cp850', errors='replace')
            if rs.status_code == 0: return True, stdout
            else: return False, stderr
        except Exception as e:
            return False, str(e)
