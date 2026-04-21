param(
  [switch]$Run
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Installing backend dependencies..."
pip install -r ".\backend\requirements.txt"

Write-Host "Installing frontend dependencies..."
Push-Location ".\frontend"
npm install
Pop-Location

Write-Host "Running migrations..."
Push-Location ".\backend"
alembic -c alembic.ini upgrade head
Pop-Location

if ($Run) {
  Write-Host "Starting backend and frontend..."
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; python -m uvicorn backend.main:app --reload"
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; npm start"
  Write-Host "Services launched in new PowerShell windows."
} else {
  Write-Host "Bootstrap complete. Run with -Run to start services automatically."
}
