
                        $PC = "192.168.0.12"
                        $U = "Administrador"
                        $P = "dsP3026x&"
                        $SecPass = ConvertTo-SecureString $P -AsPlainText -Force
                        $Cred = New-Object System.Management.Automation.PSCredential ($U, $SecPass)
                        
                        try {
                            $Res = Invoke-WmiMethod -ComputerName $PC -Credential $Cred -Class Win32_Process -Name Create -ArgumentList 'cmd /c schtasks /Create /XML "C:\Windows\Temp\ha_task_import.xml" /TN "SistemaHA_Backup_Robocopy" /F > C:\Windows\Temp\schtasks_debug.log 2>&1' -ErrorAction Stop
                            if ($Res.ReturnValue -eq 0) { Write-Host "SUCCESS" } else { Write-Host "ERROR_RET: $($Res.ReturnValue)" }
                        } catch {
                            Write-Host "ERROR_EX: $($_.Exception.Message)"
                        }
                        