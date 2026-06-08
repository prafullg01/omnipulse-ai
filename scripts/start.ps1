# OmniPulse AI — Startup Script
# Run this script to start both frontend and backend

Write-Host ''
Write-Host '=============================================' -ForegroundColor 'Cyan'
Write-Host '  OMNIPULSE AI — Customer Intelligence OS' -ForegroundColor 'White'
Write-Host '=============================================' -ForegroundColor 'Cyan'
Write-Host ''

$BackendDir = Resolve-Path (Join-Path $PSScriptRoot '../backend')
$FrontendDir = Resolve-Path (Join-Path $PSScriptRoot '../frontend')
$PythonExe = Join-Path $BackendDir 'venv/Scripts/python.exe'

# Seed database
Write-Host '[1/3] Seeding database...' -ForegroundColor 'Yellow'
Push-Location $BackendDir
& $PythonExe -c 'from app.database.seed import seed_database; seed_database()'
Pop-Location

# Start backend
Write-Host '[2/3] Starting FastAPI backend on port 8000...' -ForegroundColor 'Yellow'
$backend = Start-Process -FilePath $PythonExe `
    -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload' `
    -WorkingDirectory $BackendDir `
    -PassThru -NoNewWindow

Start-Sleep -Seconds 3

# Start frontend
Write-Host '[3/3] Starting Vite dev server on port 5173...' -ForegroundColor 'Yellow'
$frontend = Start-Process -FilePath 'npm.cmd' `
    -ArgumentList 'run', 'dev' `
    -WorkingDirectory $FrontendDir `
    -PassThru -NoNewWindow

Write-Host ''
Write-Host '=============================================' -ForegroundColor 'Green'
Write-Host '  OmniPulse AI is running!' -ForegroundColor 'White'
Write-Host '' 
Write-Host '  Frontend:  http://localhost:5173' -ForegroundColor 'Cyan'
Write-Host '  Backend:   http://localhost:8000' -ForegroundColor 'Cyan'
Write-Host '  API Docs:  http://localhost:8000/docs' -ForegroundColor 'Cyan'
Write-Host ''
Write-Host '  Admin:     admin@omnipulse.ai / admin123' -ForegroundColor 'Yellow'
Write-Host '=============================================' -ForegroundColor 'Green'
Write-Host ''
Write-Host 'Press Ctrl+C to stop all services.' -ForegroundColor 'DarkGray'

# Wait for processes
try {
    Wait-Process -Id $backend.Id, $frontend.Id
} catch {
    # Cleanup on exit
    Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -ErrorAction SilentlyContinue
}
