@echo off
set ANTHROPIC_API_KEY=여기에_API_키_입력
cd /d "%~dp0"

echo [1/3] Killing old server processes on port 8001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 1 /nobreak >nul

echo [2/3] Installing dependencies...
pip install anthropic fastapi uvicorn --quiet

echo [3/3] Starting server...
python -m uvicorn server:app --host 0.0.0.0 --port 8001
pause
