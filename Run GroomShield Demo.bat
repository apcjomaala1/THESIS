@echo off
setlocal
cd /d "%~dp0"
title GroomShield Demo Server

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH. Install Python or add it to PATH, then try again.
    pause
    exit /b 1
)

rem Reuse an already-running demo instead of creating a second server on port 5000.
powershell.exe -NoProfile -WindowStyle Hidden -Command "$url='http://127.0.0.1:5000'; try { $response=Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; if($response.StatusCode -eq 200) { Start-Process $url; exit 0 } } catch {}; exit 1"
if not errorlevel 1 (
    echo GroomShield is already running. Opened it in your browser.
    exit /b 0
)

echo Starting GroomShield. The browser will open when the server is ready.
echo Keep this window open while using the demo. Press Ctrl+C to stop it.

start "" /min powershell.exe -NoProfile -WindowStyle Hidden -Command "$url='http://127.0.0.1:5000'; $until=(Get-Date).AddMinutes(3); while((Get-Date) -lt $until) { try { $response=Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing; if($response.StatusCode -eq 200) { Start-Process $url; exit 0 } } catch {}; Start-Sleep -Seconds 1 }"
python -u run_live_demo.py

echo.
echo Demo server stopped.
pause
