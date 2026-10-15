"""
Image processing utilities using OpenCV
"""
import cv2
import numpy as np
from typing import Tuple
from io import BytesIO
from PIL import Image


def decode_image(file_bytes: bytes) -> np.ndarray:
    """
    Decode image bytes to OpenCV format (BGR)
    
    Args:
        file_bytes: Raw image bytes
        
    Returns:
        OpenCV image array (BGR format)
        
    Raises:
        ValueError: If image cannot be decoded
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(file_bytes, np.uint8)
    
    # Decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Failed to decode image. Invalid image format.")
    
    return img


def preprocess_for_yolo(image: np.ndarray, target_size: Tuple[int, int] = (640, 640)) -> np.ndarray:
    """
    Preprocess image for YOLO inference
    YOLO models typically expect RGB format and specific size
    
    Args:
        image: OpenCV image (BGR)
        target_size: Target size for YOLO (width, height)
        
    Returns:
        Preprocessed image ready for YOLO
    """
    # Convert BGR to RGB (YOLO expects RGB)
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize while maintaining aspect ratio (YOLO handles this internally)
    # But we can optionally resize here if needed
    return img_rgb


def validate_image(file_bytes: bytes) -> bool:
    """
    Validate if bytes represent a valid image
    
    Args:
        file_bytes: Raw image bytes
        
    Returns:
        True if valid image, False otherwise
    """
    try:
        decode_image(file_bytes)
        return True
    except Exception:
        return False
