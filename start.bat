@echo off
echo ========================================================
echo  Starting Disaster Response Intelligence Platform
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/2] Launching Backend Server (FastAPI on http://127.0.0.1:8000)...
start "Disaster Response - Backend" cmd /k "cd /d "%~dp0backend" && .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching Frontend Server (Vite on http://localhost:5173)...
start "Disaster Response - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================================
echo  Both services launched successfully!
echo   - Frontend:     http://localhost:5173
echo   - Backend Docs: http://127.0.0.1:8000/docs
echo   - API Base:     http://127.0.0.1:8000
echo ========================================================
pause
