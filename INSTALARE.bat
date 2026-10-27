@echo off
cd /d "%~dp0"
py -3.12 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements-simple.txt
if errorlevel 1 goto fail
echo Instalare terminata. Foloseste PORNIRE.bat pentru modul simplu.
pause
exit /b 0
:fail
echo Instalarea a esuat. Instaleaza Python 3.12 pe 64 biti de pe python.org.
pause
exit /b 1
