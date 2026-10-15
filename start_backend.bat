@echo off
REM Start Backend Server Script

echo ================================
echo Starting Backend Server
echo ================================
echo.

cd backend

REM Check if weights exist
if not exist "weights\best.pt" (
    echo [93m WARNING: Model weights not found! [0m
    echo.
    echo You need to train a model first:
    echo   cd ml_pipeline
    echo   python quickstart_training.py
    echo.
    echo Or download a placeholder model for testing
    echo.
    pause
    exit /b 1
)

echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
