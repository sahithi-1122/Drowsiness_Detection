"""
Model management and loading
This module abstracts model loading so the underlying architecture can be swapped
"""
import os
from pathlib import Path
from typing import Optional, Protocol
from ultralytics import YOLO
import torch


class ModelInterface(Protocol):
    """
    Protocol defining the interface any model must implement
    This allows swapping YOLO for other architectures (CNN, etc.) without breaking the API
    """
    def predict(self, image, **kwargs):
        """Run inference on an image"""
        ...


class YOLOModel:
    """
    YOLO model wrapper implementing the ModelInterface
    """
    def __init__(self, model_path: str):
        """
        Initialize YOLO model
        
        Args:
            model_path: Path to YOLO weights file (.pt)
        """
        path = Path(model_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[2] / path
        if not path.is_file():
            raise FileNotFoundError(f"Model weights not found at {path}")
        
        # Load YOLO model
        self.model = YOLO(str(path))

        class_names = {str(name).lower().replace("-", "_") for name in self.model.names.values()}
        if not ({"drowsy", "alert", "non_drowsy"} & class_names):
            raise ValueError(
                "The configured model is not a drowsiness classifier. "
                "Expected a Drowsy/Alert/Non_Drowsy class."
            )
        
        # Set device (use GPU if available)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        
        print(f"✓ YOLO model loaded from {path}")
        print(f"✓ Using device: {self.device}")
    
    def predict(self, image, conf_threshold: float = 0.25, **kwargs):
        """
        Run YOLO inference
        
        Args:
            image: Input image (numpy array, RGB format)
            conf_threshold: Confidence threshold
            **kwargs: Additional YOLO-specific parameters
            
        Returns:
            YOLO Results object
        """
        results = self.model.predict(
            source=image,
            conf=conf_threshold,
            verbose=False,
            **kwargs
        )
        return results


class ModelManager:
    """
    Singleton model manager - ensures model is loaded only once
    """
    _instance: Optional['ModelManager'] = None
    _model: Optional[ModelInterface] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self, model_path: str, model_type: str = "yolo") -> None:
        """
        Load model at startup
        
        Args:
            model_path: Path to model weights
            model_type: Type of model ("yolo", "cnn", etc.)
        """
        if self._model is not None:
            print("⚠ Model already loaded, skipping...")
            return
        
        if model_type == "yolo":
            self._model = YOLOModel(model_path)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def get_model(self) -> ModelInterface:
        """
        Get loaded model instance
        
        Returns:
            Loaded model
            
        Raises:
            RuntimeError: If model not loaded
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self._model
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._model is not None


# Global model manager instance
model_manager = ModelManager()
