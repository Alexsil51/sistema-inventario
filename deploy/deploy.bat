@echo off
REM ==================================================
REM DEPLOY CORPORATIVO - AGENTE DE INVENTÁRIO
REM ==================================================
setlocal enabledelayedexpansion

echo [%DATE% %TIME%] Iniciando instalacao do Agente de Inventario...
echo.

REM --- Configurações ---
set SERVER_IP=10.65.0.16
set DEPLOY_SHARE=\\!SERVER_IP!\InventoryDeploy
set INSTALL_DIR=C:\ProgramData\InventoryAgent
set TEMP_DIR=C:\Windows\Temp\InventoryDeploy

REM --- Criar diretório temporário ---
echo Criando diretorio temporario...
mkdir "!TEMP_DIR!" 2>nul

REM --- Copiar arquivos para temp primeiro ---
echo Copiando arquivos do servidor...
robocopy "!DEPLOY_SHARE!" "!TEMP_DIR!" InventoryAgent.exe config.json /NJH /NJS /NFL /NDL

if errorlevel 8 (
    echo ERRO: Nao foi possivel acessar o servidor !SERVER_IP!
    echo Verifique: 
    echo 1. Conexao de rede
    echo 2. Compartilhamento !DEPLOY_SHARE!
    echo 3. Permissoes de acesso
    pause
    exit /b 1
)

REM --- Criar pasta de instalacao ---
echo Criando diretorio de instalacao...
mkdir "!INSTALL_DIR!" 2>nul

REM --- Copiar arquivos para instalacao ---
copy "!TEMP_DIR!\InventoryAgent.exe" "!INSTALL_DIR!\" /Y
copy "!TEMP_DIR!\config.json" "!INSTALL_DIR!\" /Y

REM --- Verificar se arquivos foram copiados ---
if not exist "!INSTALL_DIR!\InventoryAgent.exe" (
    echo ERRO: Falha ao copiar InventoryAgent.exe
    pause
    exit /b 1
)

if not exist "!INSTALL_DIR!\config.json" (
    echo ERRO: Falha ao copiar config.json
    pause
    exit /b 1
)

REM --- Configurar tarefa agendada ---
echo Configurando tarefa agendada semanal...
schtasks /create /tn "InventoryAgent Weekly Scan" ^
    /tr "\"!INSTALL_DIR!\InventoryAgent.exe\" --silent" ^
    /sc weekly /d MON /st 02:00 ^
    /ru SYSTEM /f /rl HIGHEST 2>nul

if errorlevel 1 (
    echo AVISO: Nao foi possivel criar tarefa agendada.
    echo Executando manualmente...
)

REM --- Executar primeira coleta ---
echo Executando coleta inicial...
start /B "" "!INSTALL_DIR!\InventoryAgent.exe" --silent

REM --- Limpar temporarios ---
rd /s /q "!TEMP_DIR!" 2>nul

REM --- Verificacao final ---
echo.
echo ==================================================
echo VERIFICACAO DA INSTALACAO:
echo ==================================================
dir "!INSTALL_DIR!\"
echo.
schtasks /query /tn "InventoryAgent Weekly Scan" 2>nul && (
    echo ✅ Tarefa agendada: CONFIGURADA
) || (
    echo ❌ Tarefa agendada: FALHOU
)

echo.
echo ==================================================
echo INSTALACAO CONCLUIDA!
echo ==================================================
echo Agente: !INSTALL_DIR!\InventoryAgent.exe
echo Servidor: http://10.65.0.16:5000
echo.
echo [%DATE% %TIME%] Instalacao finalizada

REM --- Manter janela aberta apenas se executado manualmente ---
if "%1"=="" pause