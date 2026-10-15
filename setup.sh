#!/bin/bash

# Driver Drowsiness Detection - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "=================================="
echo "Driver Drowsiness Detection Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js ${NODE_VERSION} found"
else
    echo -e "${RED}✗${NC} Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo ""
echo "=================================="
echo "Installing Dependencies"
echo "=================================="
echo ""

# Backend dependencies
echo "Installing backend dependencies..."
cd backend
python3 -m pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Backend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Some backend dependencies may have failed. Check manually."
fi
cd ..

# Frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Some frontend dependencies may have failed. Check manually."
fi
cd ..

echo ""
echo "=================================="
echo "Configuring Environment"
echo "=================================="
echo ""

# Backend .env
if [ ! -f "backend/.env" ]; then
    echo "Creating backend .env file..."
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓${NC} Created backend/.env"
    echo -e "${YELLOW}→${NC} Edit backend/.env if needed"
else
    echo -e "${YELLOW}⚠${NC} backend/.env already exists (skipped)"
fi

# Frontend .env.local
if [ ! -f "frontend/.env.local" ]; then
    echo "Creating frontend .env.local file..."
    cp frontend/.env.local.example frontend/.env.local
    echo -e "${GREEN}✓${NC} Created frontend/.env.local"
    echo -e "${YELLOW}→${NC} Edit frontend/.env.local if needed"
else
    echo -e "${YELLOW}⚠${NC} frontend/.env.local already exists (skipped)"
fi

echo ""
echo "=================================="
echo "Checking Model Weights"
echo "=================================="
echo ""

# Check for model weights
if [ -f "backend/weights/best.pt" ]; then
    echo -e "${GREEN}✓${NC} Model weights found: backend/weights/best.pt"
else
    echo -e "${YELLOW}⚠${NC} Model weights NOT found"
    echo ""
    echo "Options:"
    echo "1. Train your own model:"
    echo "   cd ml_pipeline"
    echo "   python train.py --model yolo --epochs 50"
    echo "   cp models/yolo_best.pt ../backend/weights/best.pt"
    echo ""
    echo "2. Download placeholder (for testing only):"
    echo "   cd backend/weights"
    echo "   curl -L -o best.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-cls.pt"
    echo ""
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo -e "${GREEN}✓${NC} All dependencies installed"
echo -e "${GREEN}✓${NC} Configuration files created"
echo ""
echo "Next Steps:"
echo ""
echo "1. If you haven't trained a model yet:"
echo "   → See ml_pipeline/README.md for training instructions"
echo ""
echo "2. Start the backend:"
echo "   cd backend"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "For more help, see:"
echo "  → QUICKSTART.md - Quick start guide"
echo "  → README.md - Full documentation"
echo "  → DEPLOYMENT_GUIDE.md - Deploy to production"
echo ""
echo "Happy coding! 🚀"
