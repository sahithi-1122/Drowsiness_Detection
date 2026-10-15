"""
Computer Vision Features Module
Implements HOG, Sobel, Optical Flow, and Morphology operations
as specified in Project Task 6
"""
import cv2
import numpy as np
from typing import Tuple, Dict, Optional


def compute_hog_features(image: np.ndarray, cv_color_bgr2gray: int = cv2.COLOR_BGR2GRAY) -> Dict:
    """
    HOG (Histogram of Oriented Gradients) feature extraction
    Represents local gradient orientation patterns around the driver or selected face/eye region.
    
    Args:
        image: Input image (BGR or grayscale)
        cv_color_bgr2gray: Color conversion code
        
    Returns:
        Dictionary with HOG features and metadata
    """
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv_color_bgr2gray)
        else:
            gray = image.copy()
        
        # HOG parameters
        win_size = (128, 128)
        block_size = (16, 16)
        block_stride = (8, 8)
        cell_size = (8, 8)
        nbins = 9
        
        # Resize image to match HOG window size
        gray_resized = cv2.resize(gray, win_size)
        
        # Check if HOGDescriptor is available
        if not hasattr(cv2, 'HOGDescriptor'):
            # Fallback: compute simple gradient statistics
            grad_x = cv2.Sobel(gray_resized, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_resized, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            return {
                "feature_length": magnitude.size,
                "mean": float(magnitude.mean()),
                "std": float(magnitude.std()),
                "descriptor": True,
                "method": "gradient_fallback"
            }
        
        # Initialize HOG descriptor
        hog = cv2.HOGDescriptor(
            win_size,
            block_size,
            block_stride,
            cell_size,
            nbins
        )
        
        # Compute HOG features
        features = hog.compute(gray_resized)
        
        return {
            "feature_length": len(features) if features is not None else 0,
            "mean": float(features.mean()) if features is not None else 0.0,
            "std": float(features.std()) if features is not None else 0.0,
            "descriptor": True,
            "method": "hog_descriptor"
        }
    except Exception as e:
        print(f"HOG extraction error: {e}")
        return {
            "feature_length": 0,
            "mean": 0.0,
            "std": 0.0,
            "descriptor": False,
            "error": str(e)
        }


def compute_sobel_features(
    image: np.ndarray,
    cv_color_bgr2gray: int = cv2.COLOR_BGR2GRAY,
    cv_64f: int = cv2.CV_64F,
    ksize: int = 3
) -> Dict:
    """
    Sobel + thresholding for edge detection
    Extract horizontal/vertical gradients, combine into edge magnitude,
    and obtain a binary map using Otsu thresholding.
    
    Args:
        image: Input image
        cv_color_bgr2gray: Color conversion code
        cv_64f: Data type for gradients
        ksize: Kernel size for Sobel
        
    Returns:
        Dictionary with edge density and morphology flag
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv_color_bgr2gray)
    else:
        gray = image.copy()
    
    # Apply Gaussian blur to reduce noise
    gray_blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Compute Sobel gradients
    grad_x = cv2.Sobel(gray_blurred, cv_64f, 1, 0, ksize=ksize)
    grad_y = cv2.Sobel(gray_blurred, cv_64f, 0, 1, ksize=ksize)
    
    # Compute gradient magnitude
    magnitude = cv2.magnitude(grad_x, grad_y)
    magnitude = cv2.convertScaleAbs(magnitude)
    
    # Apply Otsu thresholding
    _, binary = cv2.threshold(magnitude, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Compute edge density
    edge_density = np.count_nonzero(binary) / binary.size
    
    return {
        "edge_density": float(edge_density),
        "threshold_method": "otsu",
        "morphology_flag": True
    }


def compute_optical_flow(
    previous_gray: np.ndarray,
    current_gray: np.ndarray,
    cv2_color_bgr2gray: int = cv2.COLOR_BGR2GRAY
) -> Dict:
    """
    Optical flow tracker for live monitoring
    Compare consecutive monitoring frames to estimate motion and stability.
    
    Args:
        previous_gray: Previous frame (grayscale)
        current_gray: Current frame (can be BGR or grayscale)
        cv2_color_bgr2gray: Color conversion code
        
    Returns:
        Dictionary with motion magnitude and availability flag
    """
    # Ensure both frames are grayscale
    if len(current_gray.shape) == 3:
        current_gray = cv2.cvtColor(current_gray, cv2_color_bgr2gray)
    
    # Compute dense optical flow using Farneback method
    flow = cv2.calcOpticalFlowFarneback(
        previous_gray,
        current_gray,
        None,
        pyr_scale=0.5,
        levels=3,
        winsize=15,
        iterations=3,
        poly_n=5,
        poly_sigma=1.2,
        flags=0
    )
    
    # Calculate flow magnitude
    magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    
    # Compute mean and max magnitude
    mean_magnitude = float(np.mean(magnitude))
    max_magnitude = float(np.max(magnitude))
    
    return {
        "mean_magnitude": mean_magnitude,
        "max_magnitude": max_magnitude,
        "available": True
    }


def apply_morphology(binary_image: np.ndarray, kernel_size: Tuple[int, int] = (5, 5)) -> Dict:
    """
    Morphology operations to clean binary edge map
    Remove small isolated regions and close small gaps in the binary edge map.
    
    Args:
        binary_image: Binary image from Sobel/thresholding
        kernel_size: Size of morphological kernel
        
    Returns:
        Dictionary with cleaned binary-region density and morphology flag
    """
    # Create morphological kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    
    # Apply morphological opening (erosion followed by dilation)
    # Removes small isolated regions
    opened = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
    
    # Apply morphological closing (dilation followed by erosion)
    # Closes small gaps
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    
    # Compute density
    cleaned_density = np.count_nonzero(closed) / closed.size
    
    return {
        "cleaned_density": float(cleaned_density),
        "morphology_applied": True,
        "operations": ["opening", "closing"]
    }


def extract_all_cv_features(
    current_frame: np.ndarray,
    previous_frame: Optional[np.ndarray] = None
) -> Dict:
    """
    Extract all CV features from a frame
    
    Args:
        current_frame: Current video frame (BGR)
        previous_frame: Previous frame for optical flow (optional)
        
    Returns:
        Dictionary containing all CV feature metadata
    """
    results = {
        "hog": None,
        "sobel": None,
        "optical_flow": None,
        "morphology": None
    }
    
    try:
        # 1. HOG Features
        results["hog"] = compute_hog_features(current_frame)
        
        # 2. Sobel + Thresholding
        sobel_result = compute_sobel_features(current_frame)
        results["sobel"] = sobel_result
        
        # 3. Morphology (on Sobel binary output)
        # Create binary image for morphology
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        grad_x = cv2.Sobel(gray_blurred, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray_blurred, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(grad_x, grad_y)
        magnitude = cv2.convertScaleAbs(magnitude)
        _, binary = cv2.threshold(magnitude, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        results["morphology"] = apply_morphology(binary)
        
        # 4. Optical Flow (if previous frame available)
        if previous_frame is not None:
            current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY) if len(previous_frame.shape) == 3 else previous_frame
            results["optical_flow"] = compute_optical_flow(previous_gray, current_gray)
        
    except Exception as e:
        print(f"Error extracting CV features: {e}")
    
    return results


def validate_cv_features(cv_metadata: Dict) -> Dict:
    """
    Validate CV features for demonstration
    
    Args:
        cv_metadata: Dictionary containing CV feature results
        
    Returns:
        Validation results
    """
    validation = {
        "hog_valid": False,
        "sobel_valid": False,
        "optical_flow_valid": False,
        "morphology_valid": False,
        "all_valid": False
    }
    
    # Validate HOG
    if cv_metadata.get("hog"):
        hog = cv_metadata["hog"]
        validation["hog_valid"] = hog.get("feature_length", 0) > 0
    
    # Validate Sobel
    if cv_metadata.get("sobel"):
        sobel = cv_metadata["sobel"]
        validation["sobel_valid"] = sobel.get("edge_density", 0) > 0
    
    # Validate Optical Flow
    if cv_metadata.get("optical_flow"):
        flow = cv_metadata["optical_flow"]
        validation["optical_flow_valid"] = flow.get("available", False)
    
    # Validate Morphology
    if cv_metadata.get("morphology"):
        morph = cv_metadata["morphology"]
        validation["morphology_valid"] = morph.get("morphology_applied", False)
    
    # All valid check
    validation["all_valid"] = all([
        validation["hog_valid"],
        validation["sobel_valid"],
        validation["morphology_valid"]
    ])
    
    return validation


# Example usage and testing
if __name__ == "__main__":
    # Create a test image
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Extract features
    features = extract_all_cv_features(test_image)
    
    print("CV Features Extracted:")
    print(f"HOG: {features['hog']}")
    print(f"Sobel: {features['sobel']}")
    print(f"Morphology: {features['morphology']}")
    
    # Validate
    validation = validate_cv_features(features)
    print(f"\nValidation: {validation}")
