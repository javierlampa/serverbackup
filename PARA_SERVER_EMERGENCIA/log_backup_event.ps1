<#
.SYNOPSIS
    Registra eventos de backup en el panel HA de EMERGENCIA via HTTP.
    
.DESCRIPTION
    Llama al API REST del panel web en EMERGENCIA para registrar eventos.
    Intenta primero la red 10Gb, luego la red 1Gb como fallback.
    Si ambas fallan, registra en log local para debugging.
    
.PARAMETER Action
    BACKUP_START o BACKUP_END
    
.PARAMETER Details
    Detalles adicionales del backup
    
.EXAMPLE
    .\log_backup_event.ps1 -Action "BACKUP_START" -Details "Iniciando backup automatico"
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("BACKUP_START", "BACKUP_END")]
    [string]$Action,
    
    [string]$Details = "",

    [Parameter(Mandatory = $false)]
    [ValidateSet("SUCCESS", "ERROR", "WARNING", "INFO")]
    [string]$Result
)

# Configuración de URLs del panel
$PANEL_URLS = @(
    "http://192.168.0.186:5000/api/backup_event"
)
$AUTH_TOKEN = "BACKUP_SECRET_TOKEN_2024"
$FALLBACK_LOG = "C:\backup_events_failed.log"

# Lógica inteligente para Result por defecto si no se especifica
if ([string]::IsNullOrEmpty($Result)) {
    if ($Action -eq "BACKUP_START") { $Result = "INFO" } else { $Result = "SUCCESS" }
}

try {
    # Preparar payload JSON
    $body = @{
        action  = $Action
        details = $Details
        result  = $Result
    } | ConvertTo-Json
    
    $headers = @{
        "Content-Type" = "application/json"
        "X-Auth-Token" = $AUTH_TOKEN
    }
    
    $success = $false
    $lastError = ""
    
    # Intentar con ambas redes
    foreach ($url in $PANEL_URLS) {
        try {
            $response = Invoke-RestMethod -Uri $url -Method POST -Body $body -Headers $headers -TimeoutSec 3 -ErrorAction Stop
            
            if ($response.status -eq "OK") {
                Write-Host "[OK] Evento $Action registrado en panel ($url)" -ForegroundColor Green
                $success = $true
                break
            }
        }
        catch {
            $lastError = $_.Exception.Message
            # Continuar con la siguiente URL
            continue
        }
    }
    
    # Si falló todo, registrar en log local
    if (-not $success) {
        $logMsg = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $Action | $Details | ERROR: $lastError"
        Add-Content -Path $FALLBACK_LOG -Value $logMsg
        Write-Host "[WARN] No se pudo registrar en panel. Guardado en $FALLBACK_LOG" -ForegroundColor Yellow
    }
}
catch {
    # Error crítico
    $logMsg = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $Action | $Details | CRITICAL_ERROR: $_"
    Add-Content -Path $FALLBACK_LOG -Value $logMsg
    Write-Host "[ERROR] Fallo crítico: $_" -ForegroundColor Red
}