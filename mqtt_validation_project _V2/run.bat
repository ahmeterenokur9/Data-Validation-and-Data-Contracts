@echo off
start "" python main.py
timeout /t 3 >nul
start http://localhost:8000/
start http://localhost:8000/admin
