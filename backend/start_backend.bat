@echo off
echo Starting College Assistant Backend...
echo.

REM Navigate to backend directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create a .env file with your GEMINI_API_KEY
    echo Example: GEMINI_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

REM Start the server
echo.
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo API Documentation will be available at: http://localhost:8000/docs
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
