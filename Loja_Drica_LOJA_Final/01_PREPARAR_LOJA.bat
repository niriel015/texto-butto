@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Loja Drica - Preparar Loja
py -3 preparar.py
if errorlevel 1 echo Configuracao pendente. Confira as instrucoes acima.
pause
