@echo off
title Vertex Platform - Demo
cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
  echo Criando ambiente virtual...
  python -m venv .venv
)

echo Instalando/verificando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt >nul

if not exist ".env" (
  copy .env.example .env >nul
)

echo.
echo Iniciando Vertex Platform...
echo Aguarde o navegador abrir.
start "" powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000/app/'"

".venv\Scripts\python.exe" -m uvicorn app.main:app --reload
