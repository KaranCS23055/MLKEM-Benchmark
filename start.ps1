# ML-KEM Benchmark Framework — Start Backend + Frontend
# Run: .\start.ps1

$ErrorActionPreference = 'SilentlyContinue'

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = Get-Location }

# Locate root directory containing start.ps1
if (Test-Path (Join-Path $ScriptDir "start.ps1")) {
    $RootDir = $ScriptDir
} elseif (Test-Path (Join-Path $ScriptDir "..\start.ps1")) {
    $RootDir = Resolve-Path (Join-Path $ScriptDir "..")
} else {
    $RootDir = Get-Location
}

Set-Location $RootDir

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ML-KEM Benchmark Framework - Starting Up " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Project Root: $RootDir" -ForegroundColor Gray
Write-Host ""

# ── 1. Backend (FastAPI) ──────────────────────────────────────────────────────
Write-Host "[1/2] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Yellow
$PythonExe = Join-Path $RootDir ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$backendJob = Start-Job -ScriptBlock {
    param($root, $py)
    $ErrorActionPreference = 'SilentlyContinue'
    Set-Location $root
    & $py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 2>&1
} -ArgumentList $RootDir, $PythonExe

Write-Host "      Backend Job ID: $($backendJob.Id)" -ForegroundColor Green

Start-Sleep -Seconds 2

# ── 2. Frontend (Vite + React) ────────────────────────────────────────────────
Write-Host "[2/2] Starting Vite frontend on http://localhost:3000 ..." -ForegroundColor Yellow
$frontendDir = Join-Path $RootDir "frontend"

$frontendJob = Start-Job -ScriptBlock {
    param($fDir)
    $ErrorActionPreference = 'SilentlyContinue'
    Set-Location $fDir
    npm run dev 2>&1
} -ArgumentList $frontendDir

Write-Host "      Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "--------------------------------------------" -ForegroundColor Cyan
Write-Host "  Backend API Docs  : http://localhost:8000/docs  " -ForegroundColor White
Write-Host "  Frontend Dashboard : http://localhost:3000       " -ForegroundColor White
Write-Host "--------------------------------------------" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop all services.        " -ForegroundColor Gray
Write-Host ""

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
