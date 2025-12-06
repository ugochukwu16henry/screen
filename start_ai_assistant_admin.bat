@echo off
REM AI Screen Assistant Launcher - Run as Administrator
REM This batch file starts the AI Screen Assistant with admin privileges

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    cd /d "%~dp0"
    python ai_screen_assistant.py
) else (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)

pause


