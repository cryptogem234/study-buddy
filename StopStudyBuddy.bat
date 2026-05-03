@echo off
echo Stopping Study Buddy...

taskkill /f /im uvicorn.exe >nul 2>&1

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 "') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo Done. Study Buddy has stopped.
timeout /t 2 /nobreak >nul
