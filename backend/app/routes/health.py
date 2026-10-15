"""
Health check endpoint
"""
from fastapi import APIRouter
from app.models.model import model_manager
import sys
import platform

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns service status and model loading state
    """
    model_loaded = model_manager.is_loaded()
    
    return {
        "status": "healthy" if model_loaded else "degraded",
        "service": "Driver Drowsiness Detection API",
        "version": "1.0.0",
        "model_loaded": model_loaded,
        "python_version": sys.version,
        "platform": platform.platform()
    }
