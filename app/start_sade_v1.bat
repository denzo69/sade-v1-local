@echo off
title Start Sade v1

set "APP_DIR=%~dp0"
for %%I in ("%~dp0..") do set "PROJECT_DIR=%%~fI"

set "VENV_PYTHON=%PROJECT_DIR%\.venv\Scripts\python.exe"

echo.
echo Starting Sade v1...
echo App folder: %APP_DIR%
echo Project folder: %PROJECT_DIR%
echo.

cd /d "%PROJECT_DIR%"

if exist "%VENV_PYTHON%" (
    echo Using virtual environment Python:
    echo %VENV_PYTHON%
    echo.
    "%VENV_PYTHON%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
) else (
    echo Virtual environment not found:
    echo %VENV_PYTHON%
    echo.
    echo Trying system Python instead...
    echo.
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
)

pause