@echo off
cd /d "%~dp0"
py -3.12 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo Instalare terminata. Foloseste PREVIZUALIZARE.bat, apoi PORNIRE.bat.
pause
exit /b 0
:fail
echo Instalarea a esuat. Instaleaza Python 3.12 pe 64 biti de pe python.org.
pause
exit /b 1
