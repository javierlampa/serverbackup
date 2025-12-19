### FAILOVER - ACTIVAR ESCRITURA EN EMERGENCIA ###
$ScriptsDir = "C:\HA_Panel\scripts"
& "$ScriptsDir\log_backup_event.ps1" -Action "BACKUP_START" -Details "Iniciando Failover: Habilitando escritura en discos de Emergencia" -Result "WARNING"

$Share1 = "EMERGENCIA_ARCHIVOS"
$Share2 = "EMERGENCIA_EDICION"

try {
    # 1. Quitar Solo Lectura y Dar Control Total (Escritura) a TODOS
    Revoke-SmbShareAccess -Name $Share1 -AccountName "Todos" -Force -ErrorAction SilentlyContinue
    Grant-SmbShareAccess -Name $Share1 -AccountName "Todos" -AccessRight Change -Force | Out-Null
    
    Revoke-SmbShareAccess -Name $Share2 -AccountName "Todos" -Force -ErrorAction SilentlyContinue
    Grant-SmbShareAccess -Name $Share2 -AccountName "Todos" -AccessRight Change -Force | Out-Null
    
    Write-Host "MODO EMERGENCIA (LECTURA/ESCRITURA) ACTIVADO" -ForegroundColor Red
    & "$ScriptsDir\log_backup_event.ps1" -Action "BACKUP_END" -Details "Failover completado: Escritura habilitada" -Result "SUCCESS"
} catch {
    Write-Host "Error: $_"
    & "$ScriptsDir\log_backup_event.ps1" -Action "BACKUP_END" -Details "ERROR en Failover: $($_.Exception.Message)" -Result "ERROR"
}