@echo off
title Potato AI - 100% Local Offline AI (Uncensored)
cd /d "%~dp0"
echo Starting Potato AI...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with code %ERRORLEVEL%.
    pause
)
