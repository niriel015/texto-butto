@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Loja Drica - Loja
if not exist ".venv\Scripts\python.exe" (
    echo Primeiro execute 01_PREPARAR_LOJA.bat.
    pause
    exit /b 1
)
set "HYPER_SITE_MODE=store"
echo.
echo LOJA DRICA - LOJA
echo Endereco: http://127.0.0.1:8000/
".venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
pause
