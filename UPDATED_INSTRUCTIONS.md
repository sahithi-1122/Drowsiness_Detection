# 🎯 Updated Setup Instructions

## ✅ What's Fixed

1. **uvicorn command issue** - Use Python module syntax instead
2. **Dataset download** - Now using `kagglehub` (easier, no API key needed initially)
3. **Interactive training script** - One command to download dataset and train

---

## 🚀 Complete Setup Flow

### Step 1: Install ML Pipeline Dependencies

```bash
cd ml_pipeline
pip install -r requirements.txt
```

This installs:
- `kagglehub` - Easy Kaggle dataset downloads
- `ultralytics` - YOLO
- `tensorflow` - For transfer learning models
- All other ML dependencies

### Step 2: Download Dataset & Train (ONE COMMAND)

```bash
# Interactive training - easiest way
python quickstart_training.py
```

This script will:
1. ✅ Auto-download dataset from Kaggle (first time only)
2. ✅ Let you choose model (YOLO recommended)
3. ✅ Configure training parameters
4. ✅ Start training
5. ✅ Copy weights to backend automatically

**OR download dataset separately:**

```bash
# Just download the dataset
python download_dataset.py
```

Then train manually:
```bash
python train.py --model yolo --epochs 50 --batch-size 32
```

### Step 3: Run Backend (FIXED COMMAND)

```bash
cd backend

# Use Python module syntax (not just "uvicorn")
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait for:
```
✓ Model loaded successfully!
✓ API is ready to accept requests
```

### Step 4: Run Frontend (New Terminal)

```bash
cd frontend
npm run dev
```

### Step 5: Open Browser

Navigate to: **http://localhost:3000**

---

## 📝 Important Command Fixes

### ❌ WRONG (doesn't work on Windows)
```bash
uvicorn app.main:app --reload
```

### ✅ CORRECT (use Python module)
```bash
python -m uvicorn app.main:app --reload
```

**Why?** The uvicorn script isn't in your PATH, but Python can find it as a module.

---

## 🎓 New Features

### 1. Easy Dataset Download

**Old way (required Kaggle API key setup):**
```bash
# Setup kaggle.json first
kaggle datasets download -d ismailnasri20/driver-drowsiness-dataset-ddd
unzip driver-drowsiness-dataset-ddd.zip -d data/
```

**New way (kagglehub - easier):**
```bash
python download_dataset.py
```

On first run, it will:
- Prompt for Kaggle authentication (browser-based, easy)
- Download dataset automatically
- Organize files correctly
- Show dataset statistics

### 2. Interactive Training

**Old way (manual commands):**
```bash
python train.py --model yolo --epochs 50
cp models/yolo_best.pt ../backend/weights/best.pt
```

**New way (interactive):**
```bash
python quickstart_training.py
```

Guides you through:
- Model selection
- Training configuration
- Automatic weight deployment

### 3. Flexible Data Loading

The data loader now:
- ✅ Handles different folder name variations
- ✅ Searches recursively if needed
- ✅ Works with kagglehub download paths
- ✅ Works with manual downloads

---

## 🔧 Troubleshooting

### "uvicorn not found"

**Problem:**
```
uvicorn : The term 'uvicorn' is not recognized...
```

**Solution:**
```bash
# Use Python module syntax
python -m uvicorn app.main:app --reload
```

### "Model not found"

**Problem:**
```
❌ Failed to load model: Model weights not found at weights/best.pt
```

**Solution:**

Option 1 - Train your own:
```bash
cd ml_pipeline
python quickstart_training.py
```

Option 2 - Download placeholder (testing only):
```bash
cd backend/weights
# Download YOLOv8n-cls base model
```

### "Dataset not found"

**Problem:**
```
❌ No images found in data/
```

**Solution:**
```bash
cd ml_pipeline
python download_dataset.py
```

Or if that fails:
```bash
# Manual download
# 1. Visit: https://www.kaggle.com/datasets/ismailnasri20/driver-drowsiness-dataset-ddd
# 2. Download ZIP
# 3. Extract to ml_pipeline/data/
```

### First-time Kaggle Authentication

When you run `download_dataset.py` for the first time:

1. **Browser opens** asking to authenticate with Kaggle
2. **Login** to your Kaggle account
3. **Allow access** to the dataset
4. **Download starts** automatically
5. **Credentials cached** for future use

No API token setup needed!

---

## 📊 Training Options

### Quick Training (for testing)
```bash
python quickstart_training.py
# Choose YOLO, 10 epochs, batch 32
# Takes ~10-15 minutes
```

### Full Training (for accuracy)
```bash
python train.py --model yolo --epochs 100 --batch-size 32
# Takes ~1-2 hours
```

### Transfer Learning (best accuracy)
```bash
python train.py --model mobilenet --epochs 50
# Or
python train.py --model efficientnet --epochs 50
```

---

## 🎯 Complete Workflow Summary

```bash
# 1. Install ML dependencies
cd ml_pipeline
pip install -r requirements.txt

# 2. Download dataset & train (one command)
python quickstart_training.py
# Follow prompts, wait for training

# 3. Verify weights copied
ls ../backend/weights/best.pt
# Should exist now

# 4. Start backend
cd ../backend
python -m uvicorn app.main:app --reload
# Wait for "Model loaded successfully!"

# 5. Start frontend (new terminal)
cd ../frontend
npm run dev

# 6. Open browser
# http://localhost:3000
```

---

## 📚 New Scripts

### ml_pipeline/download_dataset.py
- Downloads DDD dataset using kagglehub
- Auto-organizes files
- Shows dataset statistics
- Creates symlinks (Windows: copies files)

### ml_pipeline/quickstart_training.py
- Interactive training wizard
- Auto-downloads dataset if missing
- Guides model selection
- Auto-copies weights to backend
- One-command solution

### ml_pipeline/data_prep.py (updated)
- Flexible folder structure detection
- Handles kagglehub paths
- Recursive search if needed
- Better error messages

---

## ✨ Benefits of New Approach

### kagglehub vs Kaggle CLI

| Feature | kagglehub | Kaggle CLI |
|---------|-----------|------------|
| Setup | Browser auth | API token file |
| Downloads | Automatic | Manual unzip |
| Path handling | Automatic | Manual |
| Windows | Works great | Needs admin for symlinks |
| Easy use | ✅ Yes | ⚠️ More steps |

### Interactive Training

- ✅ No need to remember command syntax
- ✅ Automatic dataset check
- ✅ Guides configuration
- ✅ Auto-deploys weights
- ✅ Beginner-friendly

---

## 🎓 Next Steps

Once everything is running:

1. **Test the app**
   - Open http://localhost:3000
   - Allow camera access
   - Capture & analyze frames

2. **Check accuracy**
   ```bash
   cd ml_pipeline
   python evaluate.py --model-path models/yolo_best.pt --model-type yolo
   ```

3. **Deploy to production**
   - See DEPLOYMENT_GUIDE.md

4. **Customize**
   - Adjust model architecture
   - Add new features
   - Improve UI

---

## 📞 Still Having Issues?

1. **Check Python version**: `python --version` (need 3.11+)
2. **Check Node version**: `node --version` (need 18+)
3. **Reinstall dependencies**:
   ```bash
   cd backend && pip install -r requirements.txt
   cd ../frontend && npm install
   cd ../ml_pipeline && pip install -r requirements.txt
   ```
4. **Clear caches**:
   ```bash
   # Python
   find . -type d -name "__pycache__" -exec rm -r {} +
   
   # Node
   cd frontend && rm -rf node_modules && npm install
   ```

---

## 🎉 Summary

**Key Changes:**
1. ✅ Use `python -m uvicorn` instead of just `uvicorn`
2. ✅ Use `kagglehub` for easier dataset downloads
3. ✅ Use `quickstart_training.py` for interactive training
4. ✅ Automatic weight deployment

**New workflow is:**
- Easier for beginners
- Fewer manual steps
- Better error messages
- More automated

**Ready to build!** 🚀
