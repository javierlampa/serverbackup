<#
.SYNOPSIS
    Configura el BACKUP AUTOMATICO (Robocopy) en Server Global.
    
.DESCRIPTION
    Crea un script .bat oculto que ejecuta Robocopy.
    Crea una Tarea Programada en Windows que corre ese script cada 5 minutos.
    Copia D:\ -> \\EMERGENCIA\EMERGENCIA ARCHIVOS
    Copia E:\ -> \\EMERGENCIA\EMERGENCIA EDICION
    
.NOTES
    Ejecutar en: SERVERGLOBAL (192.168.0.12)
#>
$EmergencyIP = "192.168.0.13" # Usamos IP para evitar problemas de DNS en Workgroup
$LogFile = "C:\Backup_Robocopy.log"
$EmergencyUser = "Administrador"
$EmergencyPass = "dsP3026x&" # <--- ¡VERIFICAR QUE ESTA SEA LA CLAVE REAL DE EMERGENCIA!
# 1. Crear el script batch que hace el trabajo sucio
$BatchContent = @"
@echo off
set "LOG=C:\Backup_Robocopy.log"
echo. >> "%LOG%"
echo --- INICIO BACKUP %date% %time% --- >> "%LOG%"
:: Registrar evento de inicio en panel
powershell -ExecutionPolicy Bypass -File "C:\HA_Panel\scripts\log_backup_event.ps1" -Action "BACKUP_START" -Details "Iniciando backup automatico" 2>NUL
:: --- CONFIGURACION IPs ---
set "IP_10G=192.168.1.13"
set "IP_1G=192.168.0.13"
set "USER=$EmergencyUser"
:: Escapamos el ampersand para batch si es necesario, o usamos comillas
set "PASS=$EmergencyPass"
:: --- SELECCION DE RED (Flujo Lineal con GOTO) ---
echo [INTENTO 1] Probando conexion 10Gb (%IP_10G%)... >> "%LOG%"
net use \\%IP_10G%\IPC$ /user:%IP_10G%\%USER% "%PASS%" /Y >> "%LOG%" 2>&1
if %errorlevel% EQU 0 goto USE_10G
echo [FALLO] 10Gb no disponible. Probando 1Gb (%IP_1G%)... >> "%LOG%"
net use \\%IP_1G%\IPC$ /user:%IP_1G%\%USER% "%PASS%" /Y >> "%LOG%" 2>&1
if %errorlevel% EQU 0 goto USE_1G
echo [CRITICO] Ninguna red disponible. Abortando. >> "%LOG%"
powershell -ExecutionPolicy Bypass -File "C:\HA_Panel\scripts\log_backup_event.ps1" -Action "BACKUP_END" -Details "ERROR: Red no disponible" 2>NUL
exit /b 1
:USE_10G
echo [EXITO] Usando Red 10Gb. >> "%LOG%"
set "TARGET_IP=%IP_10G%"
goto START_COPY
:USE_1G
echo [EXITO] Usando Red 1Gb. >> "%LOG%"
set "TARGET_IP=%IP_1G%"
goto START_COPY
:START_COPY
:: --- EJECUCION ROBOCOPY ---
echo Destino seleccionado: \\%TARGET_IP% >> "%LOG%"
REM Copia D: (Archivos) -> Emergencia
echo [Copia Archivos] >> "%LOG%"
robocopy D:\ "\\%TARGET_IP%\EMERGENCIA_ARCHIVOS" /MIR /FFT /R:0 /W:0 /B /NP /XD "System Volume Information" "$RECYCLE.BIN" >> "%LOG%"
REM Copia E: (Edicion) -> Emergencia
echo [Copia Edicion] >> "%LOG%"
robocopy E:\ "\\%TARGET_IP%\EMERGENCIA_EDICION" /MIR /FFT /R:0 /W:0 /B /NP /XD "System Volume Information" "$RECYCLE.BIN" >> "%LOG%"
REM Desconectar
net use \\%TARGET_IP%\IPC$ /delete /Y >NUL
echo --- FIN BACKUP %date% %time% --- >> "%LOG%"
:: Registrar evento de fin en panel
powershell -ExecutionPolicy Bypass -File "C:\HA_Panel\scripts\log_backup_event.ps1" -Action "BACKUP_END" -Details "Backup completado exitosamente" 2>NUL
"@
$BatchPath = "C:\RunBackup.bat"
Set-Content -Path $BatchPath -Value $BatchContent
Write-Host "Script de copia creado en $BatchPath" -ForegroundColor Green
# 2. Crear/Actualizar la Tarea Programada
$TaskName = "SistemaHA_Backup_Robocopy"
# Verificar si la tarea ya existe
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host ">>> TAREA YA EXISTE. Preservando configuración de horarios." -ForegroundColor Yellow
    Write-Host "Solo se actualizó el archivo RunBackup.bat."
    Write-Host "Para cambiar horarios, usa el Panel Web o edita manualmente la tarea."
}
else {
    Write-Host ">>> Creando tarea programada por primera vez..." -ForegroundColor Cyan
    
    # Definir la accion (Ejecutar el bat)
    $Action = New-ScheduledTaskAction -Execute $BatchPath
    
    # Definir cuando (Cada 5 minutos por defecto)
    $Trigger = New-ScheduledTaskTrigger -AtStartup
    
    # Configuración adicional
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    
    # Crear la tarea
    Register-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -TaskName $TaskName -User "SYSTEM" -RunLevel Highest | Out-Null
    
    # Modificar para que repita cada 5 minutos
    schtasks /change /tn "$TaskName" /ri 5 /du 24:00
    
    Write-Host ">>> TAREA PROGRAMADA CREADA EXITOSAMENTE." -ForegroundColor Green
    Write-Host "El sistema copiará archivos a Emergencia cada 5 minutos."
}
Write-Host "El sistema copiará archivos a Emergencia cada 5 minutos."
Write-Host "Puedes probarlo ejecutando manualmente C:\RunBackup.bat"
Write-Host ""
Read-Host "Presione Enter para salir..."