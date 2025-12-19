from app import create_app
from app.services.remote import RemoteExecutor
import json

app = create_app()
with app.app_context():
    ip = app.config['GLOBAL_SERVER_IP']
    print(f"Testing WinRM Disk Query against {ip}...")
    executor = RemoteExecutor(ip)
    d_letter = "D:"
    cmd = f'Get-CimInstance Win32_LogicalDisk -Filter "DeviceID=\'{d_letter}\'" | Select-Object Size, FreeSpace | ConvertTo-Json'
    success, output = executor.run_ps_command(cmd)
    print(f"Success: {success}")
    print(f"Output: {output}")
