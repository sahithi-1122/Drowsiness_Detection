# Driver Drowsiness Detection - Backend API

FastAPI backend for real-time drowsiness detection.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
# ALLOWED_ORIGINS=http://localhost:3000
# MODEL_PATH=weights/best.pt

# Ensure model weights exist
# Copy trained model to weights/best.pt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

## 📡 API Endpoints

### GET `/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Driver Drowsiness Detection API",
  "version": "1.0.0",
  "model_loaded": true
}
```

### POST `/predict`
Drowsiness prediction from image

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image/jpeg or image/png)

**Response:**
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

## 🐳 Docker Deployment

```bash
# Build image
docker build -t drowsiness-api .

# Run container
docker run -p 8000:8000 \
  -e ALLOWED_ORIGINS="https://your-frontend.vercel.app" \
  -e MODEL_PATH="weights/best.pt" \
  drowsiness-api
```

## 🌐 Deploy to Render

1. **Push to GitHub**
2. **Create Web Service** on [Render](https://render.com)
3. **Configure:**
   - Repository: Your GitHub repo
   - Branch: `main`
   - Root Directory: `backend` (if monorepo)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
4. **Environment Variables:**
   ```
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   MODEL_PATH=weights/best.pt
   MODEL_TYPE=yolo
   ```

5. **Health Check:**
   - Path: `/health`
   - Port: Use `$PORT` variable

6. **Deploy!**

### Important Notes

- Render free tier has ~30-60s cold start after idle
- Include `weights/best.pt` in your repo (or download at build time)
- For large model files, consider using Render Disk or external storage

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALLOWED_ORIGINS` | Comma-separated frontend URLs | `http://localhost:3000,http://127.0.0.1:3000` |
| `MODEL_PATH` | Path to model weights | `weights/best.pt` |
| `MODEL_TYPE` | Model type (yolo/cnn) | `yolo` |
| `PORT` | Server port | `8000` |
| `MAX_IMAGE_BYTES` | Maximum uploaded image size | `10485760` |

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app & lifespan
│   ├── routes/              # API endpoints
│   │   ├── health.py        # Health check
│   │   └── predict.py       # Prediction endpoint
│   ├── models/              # Model loading
│   │   └── model.py         # Model manager singleton
│   ├── services/            # Business logic
│   │   ├── inference.py     # Inference service
│   │   └── image_processing.py  # Image utilities
│   └── utils/               # Helper functions
│       └── helpers.py
├── weights/
│   └── best.pt              # Trained YOLO weights
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 🔄 Swapping Models

The backend is designed to support multiple model architectures. To swap YOLO for a different model:

### 1. Implement Model Interface

In `app/models/model.py`, add your model class:

```python
class CustomCNNModel:
    def __init__(self, model_path: str):
        # Load your model (TensorFlow, PyTorch, ONNX, etc.)
        import tensorflow as tf
        self.model = tf.keras.models.load_model(model_path)
    
    def predict(self, image, **kwargs):
        # Preprocess
        img = cv2.resize(image, (224, 224))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)
        
        # Predict
        pred = self.model.predict(img)
        
        # Return in same format as YOLO
        class_idx = int(pred[0] > 0.5)
        confidence = float(pred[0][0] if class_idx == 1 else 1 - pred[0][0])
        
        return [{
            'probs': type('obj', (), {
                'top1': class_idx,
                'top1conf': confidence,
                'data': pred[0]
            })(),
            'names': {0: 'Non_Drowsy', 1: 'Drowsy'}
        }]
```

### 2. Register in ModelManager

```python
def load_model(self, model_path: str, model_type: str = "yolo"):
    if model_type == "yolo":
        self._model = YOLOModel(model_path)
    elif model_type == "custom_cnn":
        self._model = CustomCNNModel(model_path)
    # ...
```

### 3. Update Environment

```bash
MODEL_TYPE=custom_cnn
MODEL_PATH=weights/my_cnn_model.h5
```

The API endpoints remain unchanged!

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -F "file=@test_image.jpg"

# Or use Python
python -c "
import requests
files = {'file': open('test_image.jpg', 'rb')}
r = requests.post('http://localhost:8000/predict', files=files)
print(r.json())
"
```

## 📚 Technologies

- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **OpenCV** - Image processing
- **Ultralytics YOLO** - Object detection/classification
- **PyTorch** - Deep learning framework

## 🐛 Troubleshooting

### Model not loading
- Ensure `weights/best.pt` exists
- Check file permissions
- Verify YOLO version compatibility

### CORS errors
- Add frontend URL to `ALLOWED_ORIGINS`
- No trailing slashes in URLs
- Include protocol (http:// or https://)

### Import errors
- Run `pip install -r requirements.txt`
- Check Python version (3.11+ recommended)

### GPU not detected
- Install CUDA-compatible PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cu118`
- Verify CUDA installation: `nvidia-smi`

## 📄 License

MIT
