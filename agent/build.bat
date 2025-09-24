@echo off
echo Criando executavel do agente...
pip install pyinstaller
pyinstaller --onefile --name inventory-agent --hidden-import win32timezone agent.py
echo.
echo Executavel criado em: dist\inventory-agent.exe
echo.
echo Copie para a pasta deploy: xcopy dist\inventory-agent.exe ..\deploy\ /Y
pause