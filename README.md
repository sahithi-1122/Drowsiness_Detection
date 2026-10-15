# Driver Drowsiness Detection System

A complete end-to-end ML-powered web application for real-time driver drowsiness detection using the UTA-RLDD (UTA Real-Life Drowsiness Dataset) from Kaggle.

## 🏗️ Project Structure

```
Driver_Monitoring/
├── ml_pipeline/                    # ML training & data preparation
│   ├── data/                       # Dataset (download via Kaggle)
│   │   ├── train/
│   │   │   ├── active/            # Alert frames
│   │   │   └── fatigue/           # Drowsy frames
│   │   └── test/
│   │       ├── active/
│   │       └── fatigue/
│   ├── models/                     # Saved trained models
│   ├── outputs/                    # Training plots & metrics
│   ├── data_prep.py               # Data loading & preprocessing
│   ├── train.py                   # Model training script
│   ├── evaluate.py                # Model evaluation
│   ├── config.py                  # Training configuration
│   └── requirements.txt
│
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py                # FastAPI app & lifespan
│   │   ├── routes/
│   │   │   ├── health.py          # Health check endpoint
│   │   │   └── predict.py         # Prediction endpoint
│   │   ├── models/
│   │   │   └── model.py           # Model loading & management
│   │   ├── services/
│   │   │   ├── inference.py       # Inference logic
│   │   │   └── image_processing.py # Image preprocessing
│   │   └── utils/
│   │       └── helpers.py         # Utility functions
│   ├── weights/
│   │   └── best.pt                # Trained YOLO weights
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                       # Next.js frontend
│   ├── app/
│   │   ├── page.jsx               # Main page with webcam
│   │   ├── layout.jsx             # Root layout
│   │   └── globals.css            # Global styles
│   ├── components/
│   │   ├── Camera.jsx             # Webcam component
│   │   ├── DetectionResult.jsx    # Result display
│   │   └── Loading.jsx            # Loading indicator
│   ├── lib/
│   │   └── api.js                 # API client
│   ├── public/
│   ├── .env.local.example
│   ├── package.json
│   └── README.md
│
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Kaggle account & API token
- GPU recommended for training (CPU works but slower)

---

## 📊 Stage 1: Data Preparation & Model Training

### 1.1 Download Dataset

```bash
# Install kagglehub
pip install kagglehub

# Download UTA-RLDD dataset (will prompt for Kaggle credentials on first run)
cd ml_pipeline
python download_dataset.py
```

Dataset: https://www.kaggle.com/datasets/minhngt02/uta-rldd

### 1.2 Install ML Dependencies

```bash
cd ml_pipeline
pip install -r requirements.txt
```

### 1.3 Train the Model

```bash
# Recommended: YOLO classifier on UTA-RLDD
python train.py --epochs 50 --img-size 224

# If RAM is limited
python train.py --epochs 50 --img-size 224 --batch-size 16
```

### 1.4 Evaluate Model

```bash
python evaluate.py --model-path models/best_model.h5
```

This generates:
- Confusion matrix
- Precision, Recall, F1-Score
- ROC curve
- Test accuracy report

---

## 🔧 Stage 2: Backend Setup (FastAPI)

### 2.1 Local Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy trained model weights
cp ../ml_pipeline/models/best.pt weights/

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

### 2.2 Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Test prediction (with an image file)
curl -X POST http://localhost:8000/predict \
  -F "file=@test_image.jpg"
```

### 2.3 Deploy to Render

1. Push code to GitHub
2. Create new Web Service on [Render](https://render.com)
3. Connect your repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `ALLOWED_ORIGINS`: `https://your-frontend.vercel.app`
     - `MODEL_PATH`: `weights/best.pt`
   - **Health Check Path**: `/health`
5. Deploy!

⚠️ **Note**: Render free tier has ~30-60s cold start on first request after idle.

---

## 💻 Stage 3: Frontend Setup (Next.js)

### 3.1 Local Development

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.local.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 3.2 Deploy to Vercel

```bash
# Install Vercel CLI (optional)
npm i -g vercel

# Deploy
cd frontend
vercel

# Or use Vercel GitHub integration:
# 1. Push to GitHub
# 2. Import project in Vercel dashboard
# 3. Set environment variable:
#    NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
# 4. Deploy!
```

---

## 🔗 Stage 4: Connect Frontend & Backend

1. **Deploy Backend First** → Get Render URL (e.g., `https://drowsiness-api.onrender.com`)

2. **Configure Frontend**:
   - In Vercel dashboard → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL = https://drowsiness-api.onrender.com`
   - Redeploy frontend

3. **Configure Backend CORS**:
   - In Render dashboard → Environment Variables
   - Add: `ALLOWED_ORIGINS = https://your-app.vercel.app`
   - Redeploy backend

---

## 🧪 Local Testing (Full Stack)

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Open browser: http://localhost:3000
# Allow camera permissions
# Click "Capture Frame" to test detection
```

---

## 📦 Model Training Details

### Transfer Learning (MobileNetV2)
- **Base**: MobileNetV2 pretrained on ImageNet
- **Head**: Global Average Pooling → Dense(128) → Dropout(0.5) → Dense(1, sigmoid)
- **Training**: Freeze base → train head → fine-tune top layers
- **Expected Accuracy**: 95%+ on test set
- **Inference Speed**: ~50ms on CPU

### Custom CNN
- **Architecture**: 4 Conv blocks → Global Average Pool → Dense layers
- **Parameters**: ~1M (lightweight)
- **Expected Accuracy**: 92-94% on test set
- **Inference Speed**: ~30ms on CPU

### YOLO Classifier (Current Implementation)
- **Base**: YOLOv8n (nano)
- **Fine-tuned**: On UTA-RLDD dataset for 2-class classification (Alert / Drowsy)
- **Expected Accuracy**: 85–95% on test set (depends on CPU vs GPU)
- **Inference Speed**: ~40ms on CPU, ~10ms on GPU

---

## 🎯 Features

### Frontend
- ✅ Live webcam preview
- ✅ One-click frame capture
- ✅ Real-time prediction display
- ✅ Confidence score visualization
- ✅ Color-coded status (Green=Alert, Red=Drowsy)
- ✅ Error handling (camera permissions, network errors)
- ✅ Loading states with cold-start awareness
- ✅ Responsive design

### Backend
- ✅ FastAPI with async support
- ✅ CORS configuration
- ✅ Model loaded once at startup (lifespan)
- ✅ Clean architecture (routes/services/models separation)
- ✅ Health check endpoint
- ✅ Multipart form-data image upload
- ✅ OpenCV image decoding
- ✅ YOLO inference
- ✅ JSON prediction response
- ✅ Error handling & validation

---

## 🔄 Swapping Models

The backend is designed to be model-agnostic. To swap YOLO for a different architecture:

1. **Implement `ModelInterface`** in `backend/app/models/model.py`:
   ```python
   class CustomCNNModel:
       def __init__(self, model_path: str):
           # Load your model (TensorFlow, PyTorch, ONNX, etc.)
           pass
       
       def predict(self, image, **kwargs):
           # Run inference
           # Return results in same format
           pass
   ```

2. **Update `ModelManager.load_model()`**:
   ```python
   elif model_type == "custom_cnn":
       self._model = CustomCNNModel(model_path)
   ```

3. **Update inference service** if output format differs

The API contract (`POST /predict` → JSON response) remains unchanged.

---

## 📝 Environment Variables

### Backend (.env)
```bash
ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app
MODEL_PATH=weights/best.pt
MODEL_TYPE=yolo
PORT=8000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### Backend Issues

**Model not loading**:
- Ensure `weights/best.pt` exists
- Check `MODEL_PATH` environment variable
- Verify YOLO weights are compatible with ultralytics version

**CORS errors**:
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check for trailing slashes (should NOT have them)

**Cold start on Render**:
- First request after idle takes 30-60s
- Frontend shows "Waiting for server..." during cold start
- Use a paid plan or keep-alive service to avoid this

### Frontend Issues

**Camera not working**:
- Check browser permissions (chrome://settings/content/camera)
- Must use HTTPS in production (localhost HTTP is OK)
- Try different browser

**API connection failed**:
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running and accessible
- Check CORS configuration

---

## 📚 Technologies Used

- **ML**: TensorFlow/Keras or PyTorch, Ultralytics YOLO, OpenCV
- **Backend**: FastAPI, Uvicorn, Python 3.11
- **Frontend**: Next.js 14 (App Router), React 18, TailwindCSS
- **Deployment**: Vercel (frontend), Render (backend)
- **Dataset**: Kaggle DDD (Driver Drowsiness Dataset)

---

## 📄 License

MIT License - feel free to use for learning, portfolio, or commercial projects.

---

## 🙏 Acknowledgments

- Dataset: [Ismail Nasri - Driver Drowsiness Dataset (DDD)](https://www.kaggle.com/datasets/ismailnasri20/driver-drowsiness-dataset-ddd)
- YOLO: [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)

---

## 🔮 Future Enhancements

- [ ] Real-time video streaming (WebSocket/WebRTC)
- [ ] Eye Aspect Ratio (EAR) + CNN hybrid detection
- [ ] Temporal smoothing (N consecutive frames)
- [ ] Audio alert on drowsiness
- [ ] Session analytics dashboard
- [ ] Multi-face detection
- [ ] Mobile app (React Native)

---

**Questions?** Open an issue or reach out!
