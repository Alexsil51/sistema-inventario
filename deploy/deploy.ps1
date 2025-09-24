# deploy.ps1 - Script PowerShell para deploy corporativo
$ServerIP = "10.65.0.16"
$InstallDir = "C:\ProgramData\InventoryAgent"
$DeployShare = "\\$ServerIP\InventoryDeploy"

Write-Host "=== INSTALACAO AGENTE INVENTARIO ===" -ForegroundColor Green

# Criar diretório de instalação
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Host "Diretorio criado: $InstallDir" -ForegroundColor Yellow
}

# Copiar arquivos do servidor
try {
    Copy-Item "$DeployShare\InventoryAgent.exe" $InstallDir -Force
    Copy-Item "$DeployShare\config.json" $InstallDir -Force
    Write-Host "Arquivos copiados com sucesso" -ForegroundColor Green
}
catch {
    Write-Host "ERRO: Nao foi possível copiar arquivos: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verificar se arquivos existem
if (-not (Test-Path "$InstallDir\InventoryAgent.exe")) {
    Write-Host "ERRO: InventoryAgent.exe nao encontrado" -ForegroundColor Red
    exit 1
}

# Configurar tarefa agendada
try {
    $Action = New-ScheduledTaskAction -Execute "$InstallDir\InventoryAgent.exe" -Argument "--silent"
    $Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "02:00"
    $Principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden

    Register-ScheduledTask -TaskName "InventoryAgent Weekly Scan" `
        -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force | Out-Null
    
    Write-Host "Tarefa agendada configurada: Toda segunda-feira 02:00" -ForegroundColor Green
}
catch {
    Write-Host "AVISO: Nao foi possivel criar tarefa agendada: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Executar primeira coleta
try {
    Start-Process -FilePath "$InstallDir\InventoryAgent.exe" -ArgumentList "--silent" -WindowStyle Hidden
    Write-Host "Primeira coleta executada" -ForegroundColor Green
}
catch {
    Write-Host "AVISO: Nao foi possivel executar agente: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "=== INSTALACAO CONCLUIDA ===" -ForegroundColor Green
Write-Host "Diretorio: $InstallDir" -ForegroundColor Cyan
Write-Host "Servidor: http://$ServerIP`:5000" -ForegroundColor Cyan