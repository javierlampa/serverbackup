import os

class Config:
    SECRET_KEY = 'CLAVE_SUPER_SECRETA_PRODUCCION' # Idealmente cargar desde env var
    
    # Base de datos local en el servidor Ubuntu
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE = os.path.join(BASE_DIR, 'panel_data.db')
    
    # IPs de los Servidores Remotos
    GLOBAL_SERVER_IP = "192.168.0.12"
    EMERGENCY_SERVER_IP = "192.168.0.13"
    
    # IP de este servidor Ubuntu (para que los Windows puedan descargar el XML)
    PANEL_IP = "192.168.0.186" 
    
    # Credenciales para WinRM (Deben ser configuradas por el usuario o vars de entorno)
    # Por defecto asumimos usuario Administrador y la misma clave para ambos
    # TODO: Extraer a variables de entorno para mayor seguridad
    WINDOWS_USER = os.environ.get('WIN_USER', 'Administrador')
    WINDOWS_PASS = os.environ.get('WIN_PASS', 'dsP3026x&') 
    
    # Rutas Remotas (Scripts en el servidor Windows)
    REMOTE_SCRIPTS_DIR = r"C:\HA_Panel\scripts"
    REMOTE_TASK_NAME = "SistemaHA_Backup_Robocopy"
    REMOTE_LOG_PATH = r"C:\Backup_Robocopy.log" # Path en el servidor remoto (C$)
    
    # Discos a monitorear en el Global Server
    MONITOR_DISKS = ["D:", "E:"]
