@echo off
REM Start Nginx
start "" "C:\nginx-1.27.2\nginx.exe"

REM Start Flask app with Waitress
cd /d D:\Nam4\TieuLuan\Plagiarism_Detection_System
start "" "python" -m waitress --listen=127.0.0.1:8000 run:app

echo Application and Nginx started.
pause
