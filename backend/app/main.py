"""
FastAPI main application with lifespan management
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.models.model import model_manager
from app.routes import health, predict

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager - runs on startup and shutdown
    This ensures the model is loaded ONCE at startup
    """
    print("\n" + "="*60)
    print("🚀 Starting Driver Drowsiness Detection API")
    print("="*60 + "\n")
    
    # Load model on startup
    model_path = os.getenv("MODEL_PATH", "weights/best.pt")
    model_type = os.getenv("MODEL_TYPE", "yolo")
    
    try:
        print(f"Loading model from: {model_path}")
        model_manager.load_model(model_path, model_type)
        print("✓ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        print("⚠ API will start but predictions will fail")
    
    print("\n" + "="*60)
    print("✓ API is ready to accept requests")
    print("="*60 + "\n")
    
    yield
    
    # Cleanup on shutdown (if needed)
    print("\n🛑 Shutting down API...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Driver Drowsiness Detection API",
    description="Real-time drowsiness detection using computer vision",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)
allowed_origins = [origin.strip().rstrip("/") for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, tags=["Prediction"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Driver Drowsiness Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
