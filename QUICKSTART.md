# ⚡ Quick Start Guide

Get the Driver Drowsiness Detection system running in 10 minutes.

## 🎯 What You'll Build

A complete full-stack web app that:
- Captures webcam frames in the browser
- Sends images to a FastAPI backend
- Runs AI model inference (YOLO)
- Displays drowsiness predictions in real-time

---

## 📦 Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Webcam** - Built-in or USB camera
- **Kaggle Account** - For dataset download

---

## 🚀 5-Minute Setup (Without Training)

### Step 1: Clone & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd Driver_Monitoring

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### Step 2: Download Placeholder Model

For quick testing without training (uses base YOLO model):

```bash
cd backend/weights

# Download YOLOv8n-cls pretrained weights
curl -L -o best.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-cls.pt
```

⚠️ **Note:** This is NOT trained on drowsiness data. For real drowsiness detection, see "Full Setup" below.

### Step 3: Configure Environment

```bash
# Backend (.env)
cd backend
cp .env.example .env
# Edit .env if needed (defaults work for local)

# Frontend (.env.local)
cd ../frontend
cp .env.local.example .env.local
# Edit: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Test It!

1. Open browser: `http://localhost:3000`
2. Allow camera access
3. Click "Capture & Analyze Frame"
4. See the prediction!

✅ **You're running the app!** (But using placeholder model)

---

## 🎓 Full Setup (With Training)

For actual drowsiness detection, train on the DDD dataset:

### Step 1: Setup Kaggle API

```bash
# Install Kaggle CLI
pip install kaggle

# Get API token from https://www.kaggle.com/settings/account
# Download kaggle.json

# Linux/Mac
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Windows
mkdir %USERPROFILE%\.kaggle
move kaggle.json %USERPROFILE%\.kaggle\
```

### Step 2: Download Dataset

```bash
cd ml_pipeline

kaggle datasets download -d ismailnasri20/driver-drowsiness-dataset-ddd

# Extract
unzip driver-drowsiness-dataset-ddd.zip -d data/

# Verify structure
ls data/
# Should show: Drowsy/ and Non Drowsy/
```

### Step 3: Install ML Dependencies

```bash
cd ml_pipeline
pip install -r requirements.txt
```

### Step 4: Train Model

**Quick training (recommended for first run):**
```bash
python train.py --model yolo --epochs 50 --batch-size 32
```

This takes ~30-60 minutes on CPU, ~10-15 minutes on GPU.

**Other options:**
```bash
# Transfer learning (MobileNetV2) - Fast & accurate
python train.py --model mobilenet --epochs 50

# EfficientNet - Highest accuracy
python train.py --model efficientnet --epochs 50

# Custom CNN - Lightweight
python train.py --model custom_cnn --epochs 100
```

### Step 5: Copy Trained Weights

```bash
# After training completes:
cp models/yolo_best.pt ../backend/weights/best.pt
```

### Step 6: Run Full Stack

Now follow Steps 3-5 from "5-Minute Setup" above, but with your trained model!

---

## 📊 What to Expect

### Training Results
- **Accuracy:** 93-97% (depending on model)
- **Training time:** 30-60 min (CPU), 10-15 min (GPU)
- **Outputs:** 
  - `ml_pipeline/models/yolo_best.pt` - Trained weights
  - `ml_pipeline/outputs/` - Training plots

### Running Application
- **Backend startup:** ~5-10 seconds (model loading)
- **Inference time:** ~40-50ms per frame (CPU)
- **Frontend:** Instant load

---

## 🎨 Using the Application

### Main Features

1. **Live Camera Feed**
   - Shows real-time webcam
   - "LIVE" indicator when active

2. **Capture & Analyze**
   - Click button to capture current frame
   - Sends to backend for analysis
   - Shows loading spinner

3. **Detection Results**
   - **Drowsy:** Red card with warning icon
   - **Alert:** Green card with check icon
   - Confidence score with progress bar
   - Detailed class probabilities

4. **Backend Status**
   - Green = Connected
   - Red = Disconnected
   - Yellow = Checking

### Keyboard Shortcuts

- `Space` - Capture frame (when camera view is focused)
- `F5` - Refresh page (reload camera)

---

## 🧪 Testing

### Test Backend Directly

```bash
# Health check
curl http://localhost:8000/health

# Prediction (with test image)
curl -X POST http://localhost:8000/predict \
  -F "file=@path/to/test_image.jpg"
```

### Test Frontend API

```javascript
// Open browser console on http://localhost:3000
const response = await fetch('http://localhost:8000/health');
const data = await response.json();
console.log(data);
```

---

## 📱 Access from Phone

To test on mobile device (same WiFi network):

1. Find your computer's IP:
   ```bash
   # Linux/Mac
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

2. Update frontend `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://YOUR_IP:8000
   ```

3. Open on phone: `http://YOUR_IP:3000`

⚠️ **Note:** HTTPS required for camera on non-localhost. Use ngrok or deploy to production.

---

## 🐛 Common Issues

### "Model not found"
**Problem:** `backend/weights/best.pt` missing

**Solution:**
```bash
# Use placeholder:
cd backend/weights
curl -L -o best.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-cls.pt

# Or copy trained model:
cp ../../ml_pipeline/models/yolo_best.pt best.pt
```

### "Camera permission denied"
**Problem:** Browser blocked camera access

**Solution:**
- Chrome: chrome://settings/content/camera
- Allow for localhost
- Refresh page

### "Connection refused"
**Problem:** Backend not running

**Solution:**
```bash
cd backend
uvicorn app.main:app --reload
```

### "Module not found"
**Problem:** Dependencies not installed

**Solution:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Port already in use

**Problem:** Port 8000 or 3000 already taken

**Solution:**
```bash
# Backend - use different port
uvicorn app.main:app --reload --port 8001

# Update frontend .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8001

# Frontend - use different port
npm run dev -- -p 3001
```

---

## 📚 Project Structure

```
Driver_Monitoring/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   └── weights/     # Model weights
├── frontend/        # Next.js frontend
│   ├── app/         # Pages
│   ├── components/  # React components
│   └── lib/         # API client
└── ml_pipeline/     # Training code
    ├── data/        # Dataset
    ├── models/      # Trained models
    └── outputs/     # Training plots
```

---

## 🔄 Next Steps

### For Development
- ✅ Running locally
- ⬜ Train your own model
- ⬜ Customize UI
- ⬜ Add new features

### For Production
- ⬜ Deploy backend (Render)
- ⬜ Deploy frontend (Vercel)
- ⬜ Add custom domain
- ⬜ Set up monitoring

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment.

---

## 💡 Tips

1. **Start with placeholder model** - Test the pipeline first
2. **Train overnight** - Full training takes time
3. **Use GPU if available** - 4-5x faster training
4. **Check logs** - Backend terminal shows inference details
5. **Try different angles** - Test with various face positions

---

## 📖 Documentation

- [README.md](README.md) - Full project overview
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
- [backend/README.md](backend/README.md) - Backend API docs
- [frontend/README.md](frontend/README.md) - Frontend docs
- [ml_pipeline/README.md](ml_pipeline/README.md) - ML training docs

---

## 🆘 Getting Help

1. **Check logs** - Most errors show in terminal
2. **Read error messages** - They're helpful!
3. **Check browser console** - For frontend issues
4. **Review READMEs** - Component-specific help
5. **GitHub Issues** - Ask questions

---

## 🎉 Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Camera access granted
- [ ] Captured a frame
- [ ] Received a prediction
- [ ] Backend shows "Connected"

**All checked?** You're ready to rock! 🚀

---

**Time estimate:**
- Quick setup (placeholder): **10 minutes**
- Full setup (with training): **1-2 hours**
- Production deployment: **30 minutes**

Happy coding! 🎈
