@echo off
rem Serve src\ on http://localhost:8080 for local preview. Ctrl+C to stop.
cd /d "%~dp0..\src"
echo Open http://localhost:8080  (Ctrl+C to stop)
where py >nul 2>nul && (py -m http.server 8080) || (python -m http.server 8080)
