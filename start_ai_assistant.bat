@echo off
echo 🤖 Starting Gemini File System Assistant...
echo.

REM Set the API key
set GOOGLE_API_KEY=AIzaSyCF8rSzeF6rJjNI0pH7qUMwTw3XRvCAtvg

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if the server is running
echo 🌐 Checking if local server is running...
curl -s http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo ❌ Local server is not running!
    echo Please start the server first by running: python main.py
    echo.
    echo Would you like me to start the server for you? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo 🚀 Starting server in background...
        start "AI Server" cmd /k "python main.py"
        echo ⏳ Waiting for server to start...
        timeout /t 5 /nobreak >nul
    ) else (
        echo Please start the server manually and try again
        pause
        exit /b 1
    )
)

echo ✅ Starting AI Assistant...
echo.
python client_app.py

pause

