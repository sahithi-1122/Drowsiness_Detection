"""
Utility helper functions
"""
import os
from typing import Optional


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Get environment variable with optional default
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value


def format_prediction(label: str, confidence: float) -> dict:
    """
    Format prediction result consistently
    
    Supports both binary and 3-class classification:
    - Binary: Non_Drowsy, Drowsy
    - 3-class: Alert, Low_Vigilant, Drowsy
    
    Args:
        label: Prediction label
        confidence: Confidence score (0-1)
        
    Returns:
        Formatted prediction dictionary with:
        - label: Class name
        - confidence: Confidence score
        - status: Overall safety status
        - severity: Risk level (0=safe, 1=warning, 2=danger)
    """
    label_lower = label.lower()
    
    # Determine status and severity based on label
    if "alert" in label_lower or "non_drowsy" in label_lower:
        status = "alert"
        severity = 0  # Safe
        color = "green"
    elif "low_vigilant" in label_lower or "low vigilant" in label_lower:
        status = "low_vigilant"
        severity = 1  # Warning
        color = "yellow"
    elif "drowsy" in label_lower:
        status = "drowsy"
        severity = 2  # Danger
        color = "red"
    else:
        status = "unknown"
        severity = -1
        color = "gray"
    
    return {
        "label": label,
        "confidence": round(float(confidence), 4),
        "status": status,
        "severity": severity,
        "color": color
    }
