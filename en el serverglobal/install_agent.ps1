param(
  [Parameter(Mandatory=$true)][string]$Token,
  [string]$BaseUrl = "https://panel.diarioelzondasj.com.ar/api",
  [string]$AgentUrl = "https://panel.diarioelzondasj.com.ar/agent/agent.ps1"
)

Write-Host "== ServerAgent installer =="

# TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$root = "C:\ServerAgent"
$logs = Join-Path $root "logs"
$agent = Join-Path $root "agent.ps1"
$config = Join-Path $root "config.json"

New-Item -ItemType Directory -Path $root -Force | Out-Null
New-Item -ItemType Directory -Path $logs -Force | Out-Null

# Descargar agent.ps1 si falta
if (!(Test-Path $agent)) {
  Write-Host "Descargando agent.ps1 desde $AgentUrl ..."
  Invoke-WebRequest $AgentUrl -OutFile $agent -UseBasicParsing
}

# Guardar config
@{
  base_url = $BaseUrl
  token    = $Token
  interval_sec = 60
} | ConvertTo-Json | Out-File -FilePath $config -Encoding UTF8
Write-Host "Config guardada en $config"

# Crear/forzar tarea programada con schtasks (cada 1 minuto)
$taskName = "ServerAgent"
$cmd = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\ServerAgent\agent.ps1"'
try {
  schtasks /Delete /TN $taskName /F 2>$null | Out-Null
} catch {}

schtasks /Create /SC MINUTE /MO 1 /TN $taskName /TR $cmd /RU "SYSTEM" /RL HIGHEST /F

# Ejecutar ahora
schtasks /Run /TN $taskName
Write-Host "Tarea programada '$taskName' instalada y ejecutándose."