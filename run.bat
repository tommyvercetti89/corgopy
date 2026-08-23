@echo off
title CORGOPY - Advanced Port & Network Reconnaissance Engine
cls
python "%~dp0corgopy.py"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [-] Python calistirilirken bir hata olustu.
    pause
)
