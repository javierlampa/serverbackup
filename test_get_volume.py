import sys
import os
sys.path.append(os.getcwd())
from flask import Flask
from app.services.remote import RemoteExecutor
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

def test():
    with app.app_context():
        global_ip = app.config['GLOBAL_SERVER_IP']
        exec = RemoteExecutor(global_ip)
        # Probamos con D (sin dos puntos)
        cmd = 'Get-Volume -DriveLetter D | Select-Object Size, SizeRemaining | ConvertTo-Json'
        print(f"Probando en {global_ip}: {cmd}")
        success, output = exec.run_ps_command(cmd)
        print(f"Success: {success}")
        print(f"Output: {output}")

if __name__ == "__main__":
    test()
