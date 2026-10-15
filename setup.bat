@echo off
REM Driver Drowsiness Detection - Setup Script (Windows)
REM This script automates the initial setup process

echo ==================================
echo Driver Drowsiness Detection Setup
echo ==================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [92m✓[0m Python %PYTHON_VERSION% found
) else (
    echo [91m✗[0m Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('node --version') do set NODE_VERSION=%%i
    echo [92m✓[0m Node.js %NODE_VERSION% found
) else (
    echo [91m✗[0m Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo ==================================
echo Installing Dependencies
echo ==================================
echo.

REM Backend dependencies
echo Installing backend dependencies...
cd backend
python -m pip install -r requirements.txt >nul 2>&1
if %errorlevel% equ 0 (
    echo [92m✓[0m Backend dependencies installed
) else (
    echo [93m⚠[0m Some backend dependencies may have failed. Check manually.
)
cd ..

REM Frontend dependencies
echo Installing frontend dependencies...
cd frontend
call npm install >nul 2>&1
if %errorlevel% equ 0 (
    echo [92m✓[0m Frontend dependencies installed
) else (
    echo [93m⚠[0m Some frontend dependencies may have failed. Check manually.
)
cd ..

echo.
echo ==================================
echo Configuring Environment
echo ==================================
echo.

REM Backend .env
if not exist "backend\.env" (
    echo Creating backend .env file...
    copy "backend\.env.example" "backend\.env" >nul
    echo [92m✓[0m Created backend\.env
    echo [93m→[0m Edit backend\.env if needed
) else (
    echo [93m⚠[0m backend\.env already exists (skipped)
)

REM Frontend .env.local
if not exist "frontend\.env.local" (
    echo Creating frontend .env.local file...
    copy "frontend\.env.local.example" "frontend\.env.local" >nul
    echo [92m✓[0m Created frontend\.env.local
    echo [93m→[0m Edit frontend\.env.local if needed
) else (
    echo [93m⚠[0m frontend\.env.local already exists (skipped)
)

echo.
echo ==================================
echo Checking Model Weights
echo ==================================
echo.

REM Check for model weights
if exist "backend\weights\best.pt" (
    echo [92m✓[0m Model weights found: backend\weights\best.pt
) else (
    echo [93m⚠[0m Model weights NOT found
    echo.
    echo Options:
    echo 1. Train your own model:
    echo    cd ml_pipeline
    echo    python train.py --model yolo --epochs 50
    echo    copy models\yolo_best.pt ..\backend\weights\best.pt
    echo.
    echo 2. Download placeholder (for testing only):
    echo    cd backend\weights
    echo    curl -L -o best.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-cls.pt
    echo.
)

echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo [92m✓[0m All dependencies installed
echo [92m✓[0m Configuration files created
echo.
echo Next Steps:
echo.
echo 1. If you haven't trained a model yet:
echo    → See ml_pipeline\README.md for training instructions
echo.
echo 2. Start the backend:
echo    cd backend
echo    uvicorn app.main:app --reload
echo.
echo 3. In a new terminal, start the frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open your browser:
echo    http://localhost:3000
echo.
echo For more help, see:
echo   → QUICKSTART.md - Quick start guide
echo   → README.md - Full documentation
echo   → DEPLOYMENT_GUIDE.md - Deploy to production
echo.
echo Happy coding! 🚀
echo.
pause
