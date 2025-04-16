@echo off
title CSU VeMon - RFID Vehicle Monitoring System

cd /d "%~dp0"

:: Activate Python virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
)

:: Run the main application
python main.py

:: Show message incase of error
if errorlevel 1 pause