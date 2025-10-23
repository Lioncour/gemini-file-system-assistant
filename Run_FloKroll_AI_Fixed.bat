@echo off
echo Starting FloKroll AI Assistant...
echo.

REM Set the API key for this session
set GOOGLE_API_KEY=AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY

echo ✅ API Key set for this session
echo ✅ Starting AI Assistant...
echo.

cd /d "%~dp0"
.\dist\FloKroll_AI_Assistant.exe

echo.
echo Press any key to exit...
pause >nul

