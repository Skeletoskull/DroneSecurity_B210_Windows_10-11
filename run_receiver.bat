@echo off
REM DroneSecurity-B210 Launcher for Windows
REM This script runs the live receiver using radioconda environment

echo ========================================
echo DroneSecurity-B210 Live Receiver
echo ========================================
echo.

REM Check if radioconda is installed
if not exist "%USERPROFILE%\radioconda\Scripts\conda.exe" (
    echo ERROR: radioconda not found!
    echo Please install radioconda from: https://github.com/ryanvolz/radioconda/releases
    echo.
    pause
    exit /b 1
)

echo Starting receiver with default settings...
echo Gain: 40 dB
echo Band: 2.4 GHz only
echo.
echo Press Ctrl+C to stop
echo.

REM Run the receiver
"%USERPROFILE%\radioconda\Scripts\conda.exe" run -n base python src\droneid_receiver_live.py --gain 40 --band-2-4-only

echo.
echo Receiver stopped.
pause
