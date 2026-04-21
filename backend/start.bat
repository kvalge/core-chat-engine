@echo off
REM Start Core Chat Engine backend
cd /d "%~dp0"
set PYTHONPATH=%~dp0
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload