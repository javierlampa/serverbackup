@echo off
set "LOG=C:\Backup_Robocopy.log"
echo. >> "%LOG%"
echo --- INICIO BACKUP %date% %time% --- >> "%LOG%"

:: Registrar evento de inicio en panel
powershell -ExecutionPolicy Bypass -File "C:\HA_Panel\scripts\log_backup_event.ps1" -Action "BACKUP_START" -Details "Iniciando backup automatico" -Result "INFO" 2>NUL

:: --- CONFIGURACION IPs ---
set "IP_10G=192.168.1.13"
set "IP_1G=192.168.0.13"
set "USER=Administrador"
set "PASS=dsP3026x&"

:: --- SELECCION DE RED (Flujo Lineal con GOTO) ---
echo [INTENTO 1] Probando conexion 10Gb (%IP_10G%)... >> "%LOG%"
net use \\%IP_10G%\IPC$ /user:%IP_10G%\%USER% "%PASS%" /Y >> "%LOG%" 2>&1
if %errorlevel% EQU 0 goto USE_10G

echo [FALLO] 10Gb no disponible. Probando 1Gb (%IP_1G%)... >> "%LOG%"
net use \\%IP_1G%\IPC$ /user:%IP_1G%\%USER% "%PASS%" /Y >> "%LOG%" 2>&1
if %errorlevel% EQU 0 goto USE_1G

echo [CRITICO] Ninguna red disponible. Abortando. >> "%LOG%"
powershell -ExecutionPolicy Bypass -File "C:\HA_Panel\scripts\log_backup_event.ps1" -Action "BACKUP_END" -Details "ERROR: Red no disponible" -Result "ERROR" 2>NUL
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
set "ERRORS_FOUND=0"

REM Copia D: (Archivos) -> Emergencia
echo [Copia Archivos] >> "%LOG%"
robocopy D:\ "\\%TARGET_IP%\EMERGENCIA_ARCHIVOS" /MIR /FFT /R:0 /W:0 /B /NP /XD "System Volume Information" "$RECYCLE.BIN" >> "%LOG%"
if %ERRORLEVEL% GEQ 8 (
    echo [ERROR] Fallo al copiar D: (Codigo: %ERRORLEVEL%) >> "%LOG%"
    set "ERRORS_FOUND=1"
)

REM Copia E: (Edicion) -> Emergencia
echo [Copia Edicion] >> "%LOG%"
robocopy E:\ "\\%TARGET_IP%\EMERGENCIA_EDICION" /MIR /FFT /R:0 /W:0 /B /NP /XD "System Volume Information" "$RECYCLE.BIN" >> "%LOG%"
if %ERRORLEVEL% GEQ 8 (
    echo [ERROR] Fallo al copiar E: (Codigo: %ERRORLEVEL%) >> "%LOG%"
    set "ERRORS_FOUND=1"
)

REM Desconectar
net use \\%TARGET_IP%\IPC$ /delete /Y >NUL
echo --- FIN BACKUP %date% %time% --- >> "%LOG%"

:: Registrar evento de fin en panel
if "%ERRORS_FOUND%"=="1" (
    powershell -ExecutionPolicy Bypass -File "C:\HA_Panel\scripts\log_backup_event.ps1" -Action "BACKUP_END" -Details "Backup finalizado con ERRORES. Ver log." -Result "ERROR" 2>NUL
) else (
    powershell -ExecutionPolicy Bypass -File "C:\HA_Panel\scripts\log_backup_event.ps1" -Action "BACKUP_END" -Details "Backup completado CORRECTAMENTE" -Result "SUCCESS" 2>NUL
)
