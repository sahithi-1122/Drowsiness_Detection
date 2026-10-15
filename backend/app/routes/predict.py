"""
Prediction endpoint
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import os
import sys

from app.services.image_processing import decode_image, validate_image
from app.services.inference import predict_drowsiness
from app.services.temporal_analysis import reset_temporal_analyzer

router = APIRouter()
try:
    MAX_IMAGE_BYTES = max(1, int(os.getenv("MAX_IMAGE_BYTES", 10 * 1024 * 1024)))
except ValueError:
    MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.post("/predict")
async def predict(
    file: UploadFile = File(...), 
    extract_cv: bool = True,
    detect_eyes: bool = False,
    use_temporal: bool = True,
    previous_frame: Optional[UploadFile] = File(None),
    session_id: str = Query(default="default", min_length=1, max_length=128),
):
    """
    Predict drowsiness from uploaded image with optional CV feature extraction
    
    Args:
        file: Uploaded image file (JPEG, PNG)
        extract_cv: Extract CV features (HOG, Sobel, Optical Flow, Morphology)
        detect_eyes: Detect eye closure for enhanced drowsiness detection
        use_temporal: Use temporal analysis for smoothing predictions over time
        previous_frame: Optional previous frame for optical flow analysis
        
    Returns:
        JSON with prediction results:
        {
            "success": true,
            "prediction": {
                "label": "Drowsy" or "Alert",
                "confidence": float (0-1),
                "status": "drowsy" or "alert",
                "severity": int (0=safe, 1=warning, 2=danger),
                "color": "green", "yellow", or "red",
                "all_probs": {class_name: probability},
                "cv_features": {...},
                "cv_validation": {...},
                "eye_analysis": {...},
                "temporal_analysis": {
                    "smoothed_prediction": bool,
                    "consecutive_drowsy": int,
                    "drowsy_rate": float,
                    "temporal_alert_level": int (0-3),
                    "recommendation": str
                },
                "temporal_smoothed": bool,
                "raw_prediction": str (original prediction before temporal smoothing)
            }
        }
    """
    # Validate content type
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only JPEG, PNG, and WebP are supported."
        )
    
    try:
        # Read file bytes
        file_bytes = await file.read(MAX_IMAGE_BYTES + 1)

        if len(file_bytes) > MAX_IMAGE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Image is too large. Maximum size is {MAX_IMAGE_BYTES // (1024 * 1024)} MB."
            )
        
        # Validate image
        if not validate_image(file_bytes):
            raise HTTPException(
                status_code=400,
                detail="Invalid image file. Could not decode image."
            )
        
        # Decode current frame
        image = decode_image(file_bytes)
        
        # Decode previous frame if provided
        prev_image = None
        if previous_frame:
            if previous_frame.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/webp"]:
                raise HTTPException(status_code=400, detail="Previous frame must be a JPEG, PNG, or WebP image.")
            prev_bytes = await previous_frame.read(MAX_IMAGE_BYTES + 1)
            if len(prev_bytes) > MAX_IMAGE_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"Previous frame is too large. Maximum size is {MAX_IMAGE_BYTES // (1024 * 1024)} MB."
                )
            if validate_image(prev_bytes):
                prev_image = decode_image(prev_bytes)
        
        # Run inference with CV features, eye detection, and temporal analysis
        prediction = predict_drowsiness(
            image, 
            conf_threshold=0.25,
            extract_cv_features=extract_cv,
            detect_eyes=detect_eyes,
            use_temporal=use_temporal,
            previous_frame=prev_image,
            session_id=session_id,
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "prediction": prediction
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        print(f"Error during prediction: {type(e).__name__}: {e}", file=sys.stderr)
        
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Please try again."
        )


@router.post("/reset-temporal")
async def reset_temporal(
    session_id: str = Query(default="default", min_length=1, max_length=128)
):
    """
    Reset the temporal analyzer buffer
    
    Use this endpoint when starting a new monitoring session
    to clear historical predictions from previous sessions.
    
    Returns:
        JSON confirmation
    """
    try:
        reset_temporal_analyzer(session_id)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Temporal analyzer reset successfully"
            }
        )
    except Exception as e:
        print(f"Error resetting temporal analyzer: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail="Failed to reset temporal analyzer"
        )
