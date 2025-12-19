import sys
import os
import time
sys.path.append(os.getcwd())
from flask import Flask
from app.services.remote import RemoteExecutor
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

def test():
    with app.app_context():
        servers = [(app.config['GLOBAL_SERVER_IP'], "Global"), (app.config['EMERGENCY_SERVER_IP'], "Emerg")]
        disks = ["D:", "E:"]
        
        start_total = time.time()
        for ip, name in servers:
            print(f"\n--- Probando {name} ({ip}) ---")
            exec = RemoteExecutor(ip)
            for d in disks:
                t1 = time.time()
                cmd = f'Get-Volume -DriveLetter {d.replace(":","")} | Select-Object Size, SizeRemaining | ConvertTo-Json'
                success, output = exec.run_ps_command(cmd)
                t2 = time.time()
                print(f"Disco {d}: Success={success}, Tiempo={round(t2-t1, 2)}s")
                print(f"Output: {output}")
        
        print(f"\nTIEMPO TOTAL: {round(time.time() - start_total, 2)}s")

if __name__ == "__main__":
    test()
