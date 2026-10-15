@echo off
REM Start Frontend Server Script

echo ================================
echo Starting Frontend Server
echo ================================
echo.

cd frontend

echo Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
