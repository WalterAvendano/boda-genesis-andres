@echo off
title Servidor Boda QR & Drive
echo ========================================================
echo         INICIANDO SERVIDOR DE BODA QR ^& DRIVE
echo ========================================================
echo.
echo Presiona Ctrl+C cuando quieras detener el servidor.
echo ========================================================
echo.
"%~dp0venv\Scripts\python.exe" "%~dp0app.py"
pause
