@echo off
echo Starting FloKroll AI Assistant...
echo.
echo This will launch the AI Assistant with built-in server.
echo Please wait for the server to start...
echo.

REM Set the working directory to the script location
cd /d "%~dp0"

REM Launch the robust AI assistant
start "" "dist\FloKroll_AI_Robust.exe"

echo.
echo FloKroll AI Assistant launched!
echo The GUI should open shortly.
echo.
pause
