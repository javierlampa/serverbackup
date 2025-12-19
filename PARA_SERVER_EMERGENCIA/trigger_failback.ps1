### FAILBACK - RESTAURAR Y COPIAR A GLOBAL ###
$IP_10G = "192.168.1.12" # IP Global Red Rapida
$IP_1G = "192.168.0.12"  # IP Global Red Normal
$ScriptsDir = "C:\HA_Panel\scripts"

& "$ScriptsDir\log_backup_event.ps1" -Action "BACKUP_START" -Details "Iniciando Failback: Restaurando datos al servidor Global" -Result "INFO"

# 1. Selección de Red
Write-Host ">>> COMPROBANDO CONEXION CON GLOBAL..." -ForegroundColor Cyan
if (Test-Connection -ComputerName $IP_10G -Count 1 -Quiet) {
    $Target = $IP_10G
    Write-Host "[EXITO] Usando Red 10Gb para la restauración." -ForegroundColor Green
} else {
    $Target = $IP_1G
    Write-Host "[AVISO] Red 10Gb no disponible. Usando Red 1Gb." -ForegroundColor Yellow
}

# 2. Bloquear Escritura en Emergencia (Volver a Solo Lectura)
# Esto asegura que nadie guarde nada mientras estamos copiando
$Share1 = "EMERGENCIA_ARCHIVOS"
$Share2 = "EMERGENCIA_EDICION"
try {
    Revoke-SmbShareAccess -Name $Share1 -AccountName "Todos" -Force -ErrorAction SilentlyContinue
    Grant-SmbShareAccess -Name $Share1 -AccountName "Todos" -AccessRight Read -Force | Out-Null
    
    Revoke-SmbShareAccess -Name $Share2 -AccountName "Todos" -Force -ErrorAction SilentlyContinue
    Grant-SmbShareAccess -Name $Share2 -AccountName "Todos" -AccessRight Read -Force | Out-Null
    Write-Host "MODO SOLO LECTURA ACTIVADO EN EMERGENCIA" -ForegroundColor Green
} catch { 
    Write-Host "Error Permisos: $_" 
}

# 3. Restaurar Datos a Global (Robocopy Inverso)
Write-Host ">>> DINCRONIZANDO DATOS HACIA GLOBAL ($Target)... ESPERE..." -ForegroundColor Cyan

$err = 0
# Copia E: (Emergencia Archivos) -> Global D:
# Nota: Usamos /MIR para que el Global quede EXACTAMENTE como terminó Emergencia
cmd /c "robocopy ""E:\"" ""\\$Target\D$\"" /MIR /FFT /Z /R:2 /W:2 /NP /XD ""System Volume Information"" ""$RECYCLE.BIN"""
if ($LASTEXITCODE -ge 8) { $err = 1 }

# Copia D: (Emergencia Edicion) -> Global E:
cmd /c "robocopy ""D:\"" ""\\$Target\E$\"" /MIR /FFT /Z /R:2 /W:2 /NP /XD ""System Volume Information"" ""$RECYCLE.BIN"""
if ($LASTEXITCODE -ge 8) { $err = 1 }

if ($err -eq 0) {
    & "$ScriptsDir\log_backup_event.ps1" -Action "BACKUP_END" -Details "Failback completado: Datos sincronizados al Global vía $Target" -Result "SUCCESS"
    Write-Host ">>> RESTAURACION COMPLETADA CON EXITO." -ForegroundColor Green
} else {
    & "$ScriptsDir\log_backup_event.ps1" -Action "BACKUP_END" -Details "ERROR en Failback: Fallo en la sincronización Robocopy" -Result "ERROR"
    Write-Host ">>> ERROR EN LA RESTAURACION. Revise logs." -ForegroundColor Red
}