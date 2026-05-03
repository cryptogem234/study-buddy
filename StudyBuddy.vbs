Dim ROOT, WshShell

ROOT = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

Set WshShell = CreateObject("WScript.Shell")

' Start backend — hidden window
WshShell.Run "cmd /c cd /d """ & ROOT & "backend"" && """ & ROOT & "venv\Scripts\uvicorn.exe"" main:app --port 8000", 0, False

' Wait for backend to be ready
WScript.Sleep 4000

' Start frontend — hidden window
WshShell.Run "cmd /c cd /d """ & ROOT & "frontend"" && npm run dev", 0, False

' Wait for Vite to compile
WScript.Sleep 7000

' Open browser
WshShell.Run "http://localhost:5173"

Set WshShell = Nothing
