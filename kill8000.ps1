$conns = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$pids = ($conns).OwningProcess | Sort-Object -Unique
Write-Host "Killing PIDs on port 8000: $pids"
foreach ($p in $pids) {
    try { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } catch {}
    try { & cmd /c "taskkill /F /PID $p /T 2>nul" } catch {}
}
Start-Sleep 4
$still = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($still) { Write-Host "Still occupied" } else { Write-Host "Port 8000 is FREE" }
