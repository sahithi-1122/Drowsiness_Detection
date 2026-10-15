# Task 6 - Computer Vision Features Integration

## Overview

This document describes the Computer Vision (CV) feature components integrated as part of Project Task 6 for the Driver Drowsiness Detection System.

## Integrated CV Components

### 1. HOG (Histogram of Oriented Gradients)

**Purpose**: Represents local gradient orientation patterns around the driver or selected face/eye region.

**Implementation**: `backend/app/services/cv_features.py::compute_hog_features()`

**Features**:
- Window size: 128x128
- Block size: 16x16
- Block stride: 8x8
- Cell size: 8x8
- Number of bins: 9

**Output**:
```json
{
  "feature_length": int,
  "mean": float,
  "std": float,
  "descriptor": bool
}
```

**Use Case**: Feature extraction for face/eye region analysis to detect drowsiness patterns.

---

### 2. Sobel + Thresholding

**Purpose**: Extract horizontal/vertical gradients, combine into edge magnitude, and obtain a binary map using Otsu thresholding.

**Implementation**: `backend/app/services/cv_features.py::compute_sobel_features()`

**Features**:
- Gaussian blur for noise reduction (5x5 kernel)
- Sobel kernel size: 3
- Otsu automatic thresholding
- Edge density calculation

**Output**:
```json
{
  "edge_density": float,
  "threshold_method": "otsu",
  "morphology_flag": bool
}
```

**Use Case**: Edge detection to identify facial features and detect eye closure patterns.

---

### 3. Optical Flow

**Purpose**: Compare consecutive monitoring frames to estimate motion and stability.

**Implementation**: `backend/app/services/cv_features.py::compute_optical_flow()`

**Algorithm**: Farneback Dense Optical Flow

**Parameters**:
- Pyramid scale: 0.5
- Levels: 3
- Window size: 15
- Iterations: 3
- Polynomial neighborhood: 5
- Polynomial sigma: 1.2

**Output**:
```json
{
  "mean_magnitude": float,
  "max_magnitude": float,
  "available": bool
}
```

**Use Case**: 
- Detect head movement and instability
- Monitor frame-to-frame changes
- A low value may indicate stable frame (good for detection)
- Large values may reflect head movement, camera movement, or background changes

**State Management**: The tracker resets when monitoring stops or camera changes, preventing cross-session contamination.

---

### 4. Morphology Operations

**Purpose**: Remove small isolated regions and close small gaps in the binary edge map.

**Implementation**: `backend/app/services/cv_features.py::apply_morphology()`

**Operations**:
1. **Opening** (Erosion → Dilation): Removes small isolated regions
2. **Closing** (Dilation → Erosion): Closes small gaps

**Kernel**: 5x5 rectangular structuring element

**Output**:
```json
{
  "cleaned_density": float,
  "morphology_applied": bool,
  "operations": ["opening", "closing"]
}
```

**Use Case**: Clean binary edge maps for better feature analysis.

---

## Architecture Integration

### Task 6 Architecture Extension

```
Camera Frame
    │
    ├─── OpenCV decode ──► BGR to RGB conversion
    │
    ├─── HOG descriptor ──► Local gradient patterns
    │   └─── Feature metadata
    │
    ├─── Sobel gradients ──► Edge magnitude
    │   └─── Otsu threshold ──► Binary map
    │       └─── Morphology ──► Cleaned regions
    │
    ├─── Optical flow ──► Frame-to-frame motion
    │   └─── Farneback algorithm
    │
    └─── YOLO classification ──► Drowsiness prediction
         └─── Label + confidence + probabilities
              │
              ├─── cv_features (metadata)
              └─── cv_validation
```

### Response Structure

The `/predict` endpoint now returns enhanced metadata:

```json
{
  "success": true,
  "prediction": {
    "label": "Drowsy",
    "confidence": 0.91,
    "status": "drowsy",
    "severity": 2,
    "color": "red",
    "all_probs": {
      "Alert": 0.09,
      "Drowsy": 0.91
    },
    "cv_features": {
      "hog": {
        "feature_length": 3780,
        "mean": 0.0234,
        "std": 0.0456,
        "descriptor": true
      },
      "sobel": {
        "edge_density": 0.0876,
        "threshold_method": "otsu",
        "morphology_flag": true
      },
      "optical_flow": {
        "mean_magnitude": 2.34,
        "max_magnitude": 15.67,
        "available": true
      },
      "morphology": {
        "cleaned_density": 0.0654,
        "morphology_applied": true,
        "operations": ["opening", "closing"]
      }
    },
    "cv_validation": {
      "hog_valid": true,
      "sobel_valid": true,
      "optical_flow_valid": true,
      "morphology_valid": true,
      "all_valid": true
    }
  }
}
```

---

## API Usage

### Endpoint

**POST** `/predict`

### Parameters

- `file` (required): Image file (JPEG, PNG, WebP)
- `extract_cv` (optional, default=true): Extract CV features

### Example Request

```bash
# With CV features (default)
curl -X POST http://localhost:8000/predict \
  -F "file=@capture.jpg"

# Without CV features
curl -X POST "http://localhost:8000/predict?extract_cv=false" \
  -F "file=@capture.jpg"
```

### Python Example

```python
import requests

# Upload image with CV features
with open('capture.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict',
        files={'file': f}
    )
    
result = response.json()
print(result['prediction']['cv_features'])
```

---

## Validation Matrix (Task 6.1)

| Feature | Validation Procedure | Expected Evidence |
|---------|---------------------|-------------------|
| **HOG** | Run a valid frame through the feature function | Non-zero descriptor length and summary statistics |
| **Sobel / Morphology** | Run gradient magnitude, Otsu threshold, opening, and closing | Edge density and morphology flag in metadata |
| **Optical Flow** | Send moving consecutive frames and identical consecutive frames | Movement produces higher magnitude than identical frames |
| **Alarm** | Run continuous live monitoring with Drowsy outputs for at least five seconds | Audio/tone and visual alarm appear after the threshold |
| **Reset** | Stop monitoring or send a non-drowsy result | Alarm, streak, and previous-frame state reset |

---

## Implementation Evidence (Task 6)

### Test Results

| Test / Check | Observed Result | Interpretation |
|--------------|----------------|----------------|
| **GET /health** | `healthy; model_loaded = true` | Backend starts and configured model is available |
| **POST /predict smoke test** | `Drowsy; confidence about 0.91; severity 2` | Image decode, inference, and response formatting work end to end |
| **Model inspection** | `Alert, Drowsy, Low_Vigilant, Non_Drowsy` | Active checkpoint is a drowsiness classifier |
| **Frontend lint** | `Passed` | No ESLint warnings or errors reported |
| **Frontend build** | `Passed` | Next.js production compilation succeeds |
| **Alarm threshold** | Five seconds of continuous Drowsy status | Temporal logic present and requires live consecutive results |

---

## File Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── cv_features.py          # ⭐ NEW - CV feature extraction
│   │   ├── inference.py            # ✏️ Updated - Integrated CV features
│   │   └── image_processing.py     # Existing
│   └── routes/
│       └── predict.py              # ✏️ Updated - Added extract_cv parameter
```

---

## Scope and Limitations

### In Scope (Completed)

✅ HOG feature extraction with metadata  
✅ Sobel edge detection with Otsu thresholding  
✅ Morphology operations (opening + closing)  
✅ Optical flow for motion analysis  
✅ Integration with existing YOLO classifier  
✅ API parameter for enabling/disabling CV features  
✅ Validation functions for all CV components  

### Out of Scope (Remaining 25%)

As documented in Task 6 Section 8:

- **High Priority**:
  - Formal model evaluation (accuracy, precision, recall, F1, confusion matrix)
  - Direct eye-closure measurement using facial landmarks or dedicated eye-state model
  - Temporal robustness: smoothing, missing-frame handling, configurable thresholds
  
- **Medium Priority**:
  - Production validation: environment variables, CORS, model availability, cold starts
  - Alarm and safety UX: alarm.mp3 testing, audio permission handling, mute/reset control
  
- **Low Priority**:
  - Final documentation, session export, experiment tracking
  - Model provenance and reproducibility notes

### Important Notes

⚠️ **This is a working prototype** and must not be treated as:
- A replacement for safe driving
- Professional medical assessment
- A certified vehicle safety system

⚠️ **The alarm should be described as a warning aid** that should never encourage a driver to continue driving while drowsy. The safe action is to stop and rest.

---

## Testing the CV Features

### 1. Test HOG Extraction

```bash
cd backend
python -c "
from app.services.cv_features import compute_hog_features
import numpy as np
import cv2

# Create test image
img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
result = compute_hog_features(img)
print('HOG Features:', result)
"
```

### 2. Test Sobel + Morphology

```bash
python -c "
from app.services.cv_features import compute_sobel_features, apply_morphology
import numpy as np
import cv2

img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
sobel = compute_sobel_features(img)
print('Sobel:', sobel)

# Create binary for morphology
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
morph = apply_morphology(binary)
print('Morphology:', morph)
"
```

### 3. Test Optical Flow

```bash
python -c "
from app.services.cv_features import compute_optical_flow
import numpy as np
import cv2

# Create two similar frames
prev = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
curr = prev + np.random.randint(-5, 5, (480, 640), dtype=np.int16).astype(np.uint8)
flow = compute_optical_flow(prev, curr)
print('Optical Flow:', flow)
"
```

### 4. Test Full Integration

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# In another terminal, test with curl
curl -X POST http://localhost:8000/predict \
  -F "file=@test_image.jpg" \
  | python -m json.tool
```

---

## Performance Considerations

### Computational Cost

| Feature | Time (CPU) | Impact |
|---------|-----------|--------|
| YOLO Inference | ~40ms | Medium |
| HOG | ~5-10ms | Low |
| Sobel | ~2-3ms | Low |
| Optical Flow | ~10-15ms | Medium |
| Morphology | ~1-2ms | Low |
| **Total** | ~60-70ms | Acceptable for real-time |

### Optimization Tips

1. **Disable CV features** for faster inference:
   ```
   POST /predict?extract_cv=false
   ```

2. **GPU Acceleration**: Use GPU for YOLO and optical flow
   
3. **Frame Skipping**: Extract CV features every N frames instead of every frame

4. **Async Processing**: Run CV feature extraction in background thread

---

## References

- **Project Task 6 PDF**: Implementation specification
- **OpenCV Documentation**: https://docs.opencv.org/
- **HOG Paper**: Dalal & Triggs (2005)
- **Farneback Optical Flow**: Farneback (2003)
- **YOLO**: Ultralytics YOLOv8

---

## Team Information

**Team Number**: 25

**Team Members**:
- Vangara Sridhar — 2023BCS0106
- Suragauni Sahithi — 2023BCS0070
- Vatte Ramya Sri — 2023BCS0208
- Abhay Devanand Sawale — 2023BCS0046

**Project**: Driver Drowsiness Detection System Using Computer Vision

**Course**: CSE411 — Computer Vision

**Milestone**: Task 6 — Implementation Part 3 (~75% completion)

---

**Last Updated**: 2026-08-24  
**Status**: CV Features Integrated ✅
