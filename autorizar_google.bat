@echo off
title Autorizacion de Google Drive
echo ========================================================
echo        AUTORIZAR TU CUENTA DE GOOGLE DRIVE (15 GB)
echo ========================================================
echo.
"%~dp0venv\Scripts\python.exe" "%~dp0setup_oauth.py"
pause
