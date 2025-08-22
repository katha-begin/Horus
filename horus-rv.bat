@echo off
REM Horus-RV Launcher (Batch Version)
REM Simple launcher that calls the horus-rv.exe

echo Starting Horus-RV...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if horus-rv.exe exists
if exist "dist\horus-rv.exe" (
    echo Launching via horus-rv.exe...
    "dist\horus-rv.exe"
) else if exist "horus-rv.exe" (
    echo Launching via horus-rv.exe...
    "horus-rv.exe"
) else (
    echo Fallback: Direct launch...
    cd /d "C:\Users\ADMIN\Documents\augment-projects\Horus"
    "C:\OpenRv\_build\stage\app\bin\rv.exe" -pyeval "exec(open('rv_horus_integration.py').read())"
)
