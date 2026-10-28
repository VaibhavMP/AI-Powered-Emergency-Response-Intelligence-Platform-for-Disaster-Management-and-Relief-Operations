Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting Disaster Response Intelligence Platform" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$root = $PSScriptRoot

Write-Host "[1/2] Launching Backend Server (FastAPI on http://127.0.0.1:8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[2/2] Launching Frontend Server (Vite on http://localhost:5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; npm run dev"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Both services launched successfully!" -ForegroundColor Green
Write-Host "  - Frontend:     http://localhost:5173" -ForegroundColor White
Write-Host "  - Backend Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  - API Base:     http://127.0.0.1:8000" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
