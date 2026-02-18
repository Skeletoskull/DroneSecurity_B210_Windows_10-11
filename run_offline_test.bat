@echo off
REM DroneSecurity-B210 Offline Test
REM This script tests the decoder with sample files (no SDR hardware needed)

echo ========================================
echo DroneSecurity-B210 Offline Test
echo ========================================
echo.

echo Testing decoder with Mini 2 sample...
echo.

python src\droneid_receiver_offline.py -i samples\mini2_sm

echo.
echo ========================================
echo Test complete!
echo.
echo If you see decoded packets above, the decoder is working correctly.
echo.
pause
