# ML-KEM Benchmark Framework — Start Backend + Frontend
# Run: .\start.ps1

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ML-KEM Benchmark Framework - Starting Up " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Backend (FastAPI) ──────────────────────────────────────────────────────
Write-Host "[1/2] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
}
Write-Host "      Backend PID: $($backendJob.Id)" -ForegroundColor Green

Start-Sleep -Seconds 3

# ── 2. Frontend (Vite + React) ────────────────────────────────────────────────
Write-Host "[2/2] Starting Vite frontend on http://localhost:3000 ..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location (Join-Path $using:PWD "frontend")
    npm run dev
}
Write-Host "      Frontend PID: $($frontendJob.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "--------------------------------------------" -ForegroundColor Cyan
Write-Host "  Backend  : http://localhost:8000/docs      " -ForegroundColor White
Write-Host "  Frontend : http://localhost:3000           " -ForegroundColor White
Write-Host "--------------------------------------------" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop all services.        " -ForegroundColor Gray
Write-Host ""

# Wait and stream output from both jobs
try {
    while ($true) {
        Receive-Job $backendJob | ForEach-Object { Write-Host "[backend]  $_" -ForegroundColor DarkGray }
        Receive-Job $frontendJob | ForEach-Object { Write-Host "[frontend] $_" -ForegroundColor DarkGray }
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "`nStopping all services..." -ForegroundColor Red
    Stop-Job $backendJob, $frontendJob
    Remove-Job $backendJob, $frontendJob
}
