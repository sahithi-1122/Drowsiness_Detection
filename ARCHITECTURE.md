# 🏗️ System Architecture

Detailed technical architecture of the Driver Drowsiness Detection system.

## 📊 High-Level Overview

```
┌─────────────┐      HTTPS/WebSocket       ┌──────────────┐
│   Browser   │ ◄──────────────────────► │   Next.js    │
│  (Webcam)   │      Image Capture         │   Frontend   │
└─────────────┘                             └──────────────┘
                                                    │
                                                    │ REST API
                                                    │ (HTTPS)
                                                    ▼
                                            ┌──────────────┐
                                            │   FastAPI    │
                                            │   Backend    │
                                            └──────────────┘
                                                    │
                                                    │ Inference
                                                    ▼
                                            ┌──────────────┐
                                            │  YOLO Model  │
                                            │  (PyTorch)   │
                                            └──────────────┘
```

---

## 🔄 Data Flow

### 1. Image Capture Flow

```
User clicks "Capture"
    │
    ├─► Camera.jsx captures video frame
    │
    ├─► Convert to JPEG blob (canvas.toBlob)
    │
    ├─► Send to parent component
    │
    └─► Trigger API call
```

### 2. API Request Flow

```
Frontend (page.jsx)
    │
    ├─► lib/api.js → predictDrowsiness()
    │
    ├─► FormData with image blob
    │
    ├─► POST /predict
    │
    └─► Backend receives multipart/form-data
```

### 3. Backend Processing Flow

```
FastAPI receives request
    │
    ├─► routes/predict.py validates content-type
    │
    ├─► Read file bytes
    │
    ├─► services/image_processing.py
    │   ├─► Decode with OpenCV
    │   ├─► Validate image
    │   └─► Convert BGR → RGB
    │
    ├─► services/inference.py
    │   ├─► Get model from ModelManager
    │   ├─► Preprocess image
    │   ├─► Run YOLO inference
    │   └─► Parse results
    │
    ├─► Format response JSON
    │
    └─► Return to frontend
```

### 4. Result Display Flow

```
Frontend receives JSON response
    │
    ├─► Extract prediction data
    │
    ├─► Update state (setPrediction)
    │
    ├─► DetectionResult.jsx renders
    │   ├─► Status card (red/green)
    │   ├─► Confidence bar
    │   └─► Class probabilities
    │
    └─► User sees result
```

---

## 🧩 Component Architecture

### Frontend (Next.js)

```
app/
├── layout.jsx                 # Root layout, font, metadata
│
├── page.jsx                   # Main page component
│   ├── State management
│   │   ├── prediction
│   │   ├── isLoading
│   │   ├── error
│   │   └── backendStatus
│   │
│   ├── Effects
│   │   └── Check backend connection
│   │
│   └── Event handlers
│       └── handleCapture()
│
└── globals.css                # Tailwind + custom styles

components/
├── Camera.jsx                 # Webcam access & capture
│   ├── useRef: videoRef, canvasRef
│   ├── useState: stream, error, isReady
│   ├── useEffect: Initialize camera
│   ├── handleVideoLoaded()
│   └── captureFrame()
│
├── DetectionResult.jsx        # Result display
│   ├── Props: prediction, error
│   ├── Status indicator
│   ├── Confidence visualization
│   └── Class probabilities
│
└── Loading.jsx                # Loading spinner
    └── Props: message

lib/
└── api.js                     # API client
    ├── checkHealth()
    ├── predictDrowsiness()
    └── testConnection()
```

### Backend (FastAPI)

```
app/
├── main.py                    # Application entry point
│   ├── lifespan()            # Startup/shutdown
│   │   └── Load model once
│   ├── CORS middleware
│   └── Route registration
│
├── routes/
│   ├── health.py             # GET /health
│   │   └── Check model status
│   │
│   └── predict.py            # POST /predict
│       ├── Validate file type
│       ├── Decode image
│       ├── Run inference
│       └── Return JSON
│
├── models/
│   └── model.py              # Model management
│       ├── ModelInterface    # Protocol
│       ├── YOLOModel        # YOLO wrapper
│       └── ModelManager     # Singleton
│
├── services/
│   ├── image_processing.py   # Image utilities
│   │   ├── decode_image()
│   │   ├── preprocess_for_yolo()
│   │   └── validate_image()
│   │
│   └── inference.py          # Inference logic
│       ├── predict_drowsiness()
│       └── batch_predict()
│
└── utils/
    └── helpers.py            # Utility functions
        ├── get_env_var()
        └── format_prediction()
```

### ML Pipeline

```
ml_pipeline/
├── config.py                 # Configuration constants
│   ├── Paths
│   ├── Hyperparameters
│   └── Model configs
│
├── data_prep.py             # Data loading
│   ├── load_image_paths_and_labels()
│   ├── split_data()
│   ├── compute_class_weights()
│   ├── create_tf_dataset()
│   └── prepare_yolo_dataset()
│
├── train.py                 # Training script
│   ├── build_transfer_learning_model()
│   ├── build_custom_cnn()
│   ├── train_keras_model()
│   ├── train_yolo_model()
│   └── plot_training_history()
│
└── evaluate.py              # Evaluation script
    ├── evaluate_keras_model()
    ├── evaluate_yolo_model()
    ├── plot_confusion_matrix()
    └── plot_roc_curve()
```

---

## 🔐 Security Architecture

### API Security

```
Frontend Request
    │
    ├─► CORS check (ALLOWED_ORIGINS)
    │   └─► Reject if origin not allowed
    │
    ├─► Content-Type validation
    │   └─► Only image/jpeg, image/png
    │
    ├─► File size validation (implicit)
    │   └─► FastAPI limits request body
    │
    └─► Image validation
        └─► OpenCV decode check
```

### Environment Variables

**Backend:**
- `ALLOWED_ORIGINS` - CORS whitelist (never use *)
- `MODEL_PATH` - Model location
- `MODEL_TYPE` - Model architecture

**Frontend:**
- `NEXT_PUBLIC_API_URL` - Backend URL (public, no secrets)

**Security rules:**
- Never commit `.env` files
- Use `.env.example` for templates
- No secrets in frontend code
- HTTPS in production

---

## 📡 API Contract

### POST /predict

**Request:**
```http
POST /predict HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
Origin: https://allowed-origin.com

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="capture.jpg"
Content-Type: image/jpeg

[binary image data]
------WebKitFormBoundary--
```

**Success Response (200):**
```json
{
  "success": true,
  "prediction": {
    "label": "Drowsy",
    "confidence": 0.9234,
    "status": "drowsy",
    "all_probs": {
      "Non_Drowsy": 0.0766,
      "Drowsy": 0.9234
    }
  }
}
```

**Error Response (400):**
```json
{
  "detail": "Invalid file type: application/pdf. Only JPEG and PNG are supported."
}
```

**Error Response (500):**
```json
{
  "detail": "Prediction failed: Model not loaded"
}
```

---

## 🧠 Model Architecture

### YOLO Classification (Current)

```
Input Image (RGB)
    │
    ├─► Resize to 640x640 (maintain aspect)
    │
    ├─► Normalize (0-1)
    │
    ├─► YOLOv8n Backbone
    │   ├─► Conv layers
    │   ├─► C2f blocks
    │   └─► SPPF
    │
    ├─► Classification Head
    │   ├─► Global Average Pooling
    │   ├─► Dropout
    │   └─► Linear (num_classes)
    │
    ├─► Softmax
    │
    └─► Output: [Non_Drowsy_prob, Drowsy_prob]
```

**Model Stats:**
- Parameters: ~2.7M
- Size: ~6 MB
- Inference: ~40ms (CPU), ~10ms (GPU)
- Architecture: YOLOv8n-cls

### Alternative: MobileNetV2 (Optional)

```
Input Image (224x224x3)
    │
    ├─► Preprocess (ImageNet normalization)
    │
    ├─► MobileNetV2 Base (frozen)
    │   ├─► Inverted Residual Blocks
    │   └─► Depthwise Separable Convs
    │
    ├─► Global Average Pooling
    │
    ├─► Dense(128, relu)
    │
    ├─► Dropout(0.5)
    │
    ├─► Dense(1, sigmoid)
    │
    └─► Output: Drowsy_probability
```

**Model Stats:**
- Parameters: ~3.5M
- Size: ~14 MB
- Inference: ~50ms (CPU)
- Architecture: MobileNetV2 + custom head

---

## 🔄 State Management

### Frontend State Flow

```
Initial State:
├─► prediction: null
├─► isLoading: false
├─► error: null
└─► backendStatus: 'checking'

User clicks capture:
├─► isLoading = true
├─► error = null
└─► prediction = null

API call succeeds:
├─► prediction = result.prediction
├─► isLoading = false
└─► backendStatus = 'connected'

API call fails:
├─► error = error.message
├─► isLoading = false
└─► backendStatus = 'disconnected'
```

### Backend State Management

```
Server Startup:
├─► lifespan() context manager
├─► ModelManager.load_model()
├─► model_manager._model = YOLOModel
└─► Model cached in memory (singleton)

Request Processing:
├─► model_manager.get_model()
├─► Returns cached model
└─► No reloading per request
```

---

## 🚀 Performance Optimization

### Frontend Optimizations

1. **Code Splitting**
   - Next.js automatic code splitting
   - Route-based chunking

2. **Image Optimization**
   - Canvas compression (JPEG 95%)
   - Reasonable resolution (1280x720)

3. **Asset Optimization**
   - Next.js automatic font optimization
   - Tailwind CSS purging (unused styles removed)

4. **Caching**
   - Browser caches static assets
   - Service worker (future enhancement)

### Backend Optimizations

1. **Model Loading**
   - Load once at startup (not per request)
   - Singleton pattern
   - Lifespan context manager

2. **Image Processing**
   - OpenCV (C++ backend, fast)
   - No unnecessary copies
   - Efficient BGR→RGB conversion

3. **Inference**
   - GPU acceleration (if available)
   - Batch inference support
   - FP16 precision (future)

4. **API Response**
   - JSON serialization
   - Minimal response payload
   - No base64 encoding (unnecessary)

---

## 📊 Scalability Considerations

### Horizontal Scaling

**Current (Single Instance):**
```
Client → Backend Instance → Model
```

**Future (Load Balanced):**
```
                 ┌─► Backend 1 → Model 1
Client → LB ─────┼─► Backend 2 → Model 2
                 └─► Backend 3 → Model 3
```

**Considerations:**
- Each instance loads model (6MB × N)
- Stateless design (no session storage)
- Health checks per instance

### Vertical Scaling

**Options:**
- Increase RAM (for larger models)
- Add GPU (10x faster inference)
- Increase CPU cores (parallel requests)

### Caching Strategy (Future)

```
Client Request
    │
    ├─► Check Redis cache (image hash)
    │   ├─► Hit: Return cached result
    │   └─► Miss: Continue
    │
    ├─► Run inference
    │
    ├─► Cache result (TTL: 5 min)
    │
    └─► Return to client
```

---

## 🧪 Testing Architecture

### Unit Tests (Future)

```
backend/tests/
├── test_image_processing.py
│   ├── test_decode_image()
│   ├── test_preprocess_for_yolo()
│   └── test_validate_image()
│
├── test_inference.py
│   ├── test_predict_drowsiness()
│   └── test_batch_predict()
│
└── test_api.py
    ├── test_health_endpoint()
    └── test_predict_endpoint()
```

### Integration Tests (Future)

```
tests/integration/
├── test_end_to_end.py
│   ├── Upload image
│   ├── Check response format
│   └── Validate prediction
│
└── test_model_loading.py
    └── Verify model loads correctly
```

---

## 📈 Monitoring & Observability

### Metrics to Track

**Backend:**
- Request latency (p50, p95, p99)
- Model inference time
- Error rate
- Request rate (rpm)
- Model load time

**Frontend:**
- Page load time
- API call success rate
- Camera initialization time
- User interactions

### Logging Strategy

**Backend logs:**
```python
# Startup
✓ Model loaded successfully!
✓ API is ready to accept requests

# Request
[INFO] Prediction request received
[INFO] Image decoded: 640x480
[INFO] Inference time: 42ms
[INFO] Prediction: Drowsy (0.9234)

# Error
[ERROR] Failed to decode image: Invalid format
```

**Frontend logs:**
```javascript
// Console
✓ Camera initialized
✓ Backend connected
⚠ Backend disconnected (cold start?)
❌ Prediction failed: Network error
```

---

## 🔮 Future Enhancements

### Architecture Improvements

1. **WebSocket for Real-Time**
   ```
   Client ←─ WebSocket ─→ Backend
      │
      ├─► Stream video frames
      ├─► Receive predictions
      └─► Lower latency
   ```

2. **Model Serving Layer**
   ```
   Backend → TensorFlow Serving / TorchServe
      │
      ├─► Optimized inference
      ├─► Model versioning
      └─► A/B testing
   ```

3. **Edge Deployment**
   ```
   Browser
      │
      ├─► TensorFlow.js model
      ├─► Client-side inference
      └─► No server needed
   ```

4. **Microservices**
   ```
   ┌─► Auth Service
   ├─► Inference Service
   ├─► Analytics Service
   └─► Notification Service
   ```

---

## 📚 Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend Framework | Next.js 14 | React framework, SSR |
| UI Library | React 18 | Component-based UI |
| Styling | Tailwind CSS | Utility-first CSS |
| Backend Framework | FastAPI | Async Python web framework |
| Web Server | Uvicorn | ASGI server |
| ML Framework | PyTorch | Deep learning |
| Model | YOLOv8 | Object classification |
| Image Processing | OpenCV | Computer vision |
| Deployment (Backend) | Render | Cloud platform |
| Deployment (Frontend) | Vercel | Serverless platform |

---

## 🎓 Design Patterns Used

1. **Singleton Pattern**
   - ModelManager (single model instance)

2. **Protocol Pattern**
   - ModelInterface (swappable models)

3. **Service Layer Pattern**
   - Separation of concerns (routes/services/models)

4. **Dependency Injection**
   - Environment variables
   - Model manager instance

5. **Context Manager**
   - FastAPI lifespan
   - Resource cleanup

6. **Component Pattern**
   - React components
   - Reusable UI pieces

---

**Architecture Version:** 1.0.0  
**Last Updated:** 2026-08-17
