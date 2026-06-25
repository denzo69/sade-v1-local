@echo off
setlocal
title Create Sade v1 user

set "PROJECT_DIR=%~dp0.."
set "PYTHON=%PROJECT_DIR%\.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo Virtual environment Python not found: %PYTHON%
    pause
    exit /b 1
)

set /p "SADE_USERNAME=Kayttajanimi, esimerkiksi jani: "
if "%SADE_USERNAME%"=="" (
    echo Kayttajanimi puuttuu.
    pause
    exit /b 1
)

cd /d "%PROJECT_DIR%"
"%PYTHON%" -m app.auth create-user "%SADE_USERNAME%"

echo.
pause
endlocal
