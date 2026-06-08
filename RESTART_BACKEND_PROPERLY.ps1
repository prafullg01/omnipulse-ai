Write-Host "============================================" -ForegroundColor Cyan
Write-Host "OMNIPULSE AI - Clean Backend Restart" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Killing all existing Python processes on port 8000..." -ForegroundColor Yellow
$connections = netstat -ano | Select-String ":8000.*LISTENING"
$pids = @()
foreach ($conn in $connections) {
    $parts = $conn -split '\s+' | Where-Object { $_ -ne '' }
    $pid = $parts[-1]
    if ($pid -and $pid -match '^\d+$' -and $pids -notcontains $pid) {
        $pids += $pid
        Write-Host "  Killing process ID: $pid" -ForegroundColor Red
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "Step 2: Waiting 2 seconds for cleanup..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Step 3: Starting fresh backend server..." -ForegroundColor Yellow
Set-Location -Path "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Set-Location -Path ".."

Write-Host ""
Write-Host "Step 4: Waiting 5 seconds for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Step 5: Verifying server is responding..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/analytics/roi" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  SUCCESS! Total Revenue: ₹$($data.total_revenue)" -ForegroundColor Green
    Write-Host "  Campaign Revenue: ₹$($data.campaign_revenue)" -ForegroundColor Green
    Write-Host "  Revenue Protected: ₹$($data.revenue_protected)" -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Server may still be starting up..." -ForegroundColor Red
    Write-Host "  Wait a few more seconds and try accessing http://localhost:8000/api/analytics/roi" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Backend restart complete!" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Now refresh your browser with: Ctrl+Shift+R (or Cmd+Shift+R on Mac)" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
