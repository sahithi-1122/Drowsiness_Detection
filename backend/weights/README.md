# Model Weights

This directory should contain your trained model weights.

## 📦 Expected Files

- `best.pt` - Trained YOLO model weights (required)

## 🎓 Training the Model

1. Navigate to the ML pipeline directory:
   ```bash
   cd ../ml_pipeline
   ```

2. Follow the training instructions in `ml_pipeline/README.md`

3. Copy the trained weights here:
   ```bash
   cp ml_pipeline/models/yolo_best.pt backend/weights/best.pt
   ```

## 🔄 Alternative: Use Pre-trained Weights

If you don't have trained weights yet, you can start with a base YOLO model for testing:

```bash
# This will download YOLOv8n-cls pretrained on ImageNet
# Note: This is NOT trained on the drowsiness dataset!
python -c "from ultralytics import YOLO; YOLO('yolov8n-cls.pt').save('best.pt')"
```

However, this won't give accurate drowsiness predictions. You **must** train on the UTA-RLDD dataset for real drowsiness detection.

## 📏 Model Size

Expected file size: 5-10 MB for YOLOv8n-cls

If using Git LFS for large files:
```bash
git lfs track "*.pt"
git add .gitattributes
```

## 🚀 Quick Start (Development)

For local testing without training:

1. Download a placeholder model:
   ```bash
   curl -L -o best.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-cls.pt
   ```

2. Update backend to handle missing model gracefully (already implemented in `app/main.py`)

## ⚠️ Important

- Never commit sensitive or proprietary model weights to public repositories
- For production, ensure the model is trained on the correct dataset
- Model file must be named `best.pt` or update `MODEL_PATH` env var
