# ML Pipeline — Driver Drowsiness Detection

Training pipeline for the YOLOv8n-cls drowsiness detector.

## Dataset

**UTA-RLDD (UTA Real-Life Drowsiness Dataset)**
Source: https://www.kaggle.com/datasets/minhngt02/uta-rldd

Classes (binary):
- `active`  → **Alert**  (label 0)
- `fatigue` → **Drowsy** (label 1)

Dataset structure after download:
```
data/
├── train/
│   ├── active/      # Alert frames
│   └── fatigue/     # Drowsy frames
└── test/
    ├── active/
    └── fatigue/
```

## Quick Start

### 1. Install dependencies
```bash
cd ml_pipeline
pip install -r requirements.txt
```

### 2. Download dataset
```bash
python download_dataset.py
```
kagglehub will prompt for Kaggle credentials on first run.
Get your API token from: https://www.kaggle.com/settings/account

### 3. Train (interactive)
```bash
python quickstart_training.py
```

### 3. Prepare the supplied splits
```bash
python prepare_grouped_dataset.py
```
This maps `active`/`fatigue` to `Alert`/`Drowsy` while preserving the Kaggle
train/validation/test folders. It is not a participant-level split unless the
dataset provider's split metadata confirms participants are separated.

### 4. Train (manual)
```bash
# Recommended settings
python train.py --epochs 50 --img-size 224

# If you have limited RAM
python train.py --epochs 50 --img-size 224 --batch-size 16
```

### 5. Evaluate
```bash
python evaluate.py --model-path models/yolo_best.pt
```

### 6. Deploy to backend
Training automatically copies the best weights to `backend/weights/best.pt`.
If it didn't happen, copy manually:
```bash
cp models/yolo_best.pt ../backend/weights/best.pt
```

## Configuration

Edit `config.py` to customise:

```python
BATCH_SIZE              = 32
EPOCHS                  = 50
YOLO_IMG_SIZE           = 224
EARLY_STOPPING_PATIENCE = 10
```

## Expected accuracy

| Hardware | Time/epoch | 50 epochs | Expected accuracy |
|---|---|---|---|
| CPU | ~13–15 min | ~11 h | 85–90% |
| GPU (CUDA) | ~1–2 min | ~1–1.5 h | 90–95% |

## Technologies

- PyTorch + Ultralytics YOLO
- OpenCV, scikit-learn
- kagglehub

## Acknowledgements

Dataset: [minhngt02 — UTA-RLDD](https://www.kaggle.com/datasets/minhngt02/uta-rldd)
Original paper: Ghoddoosian et al., "A Realistic Dataset and Baseline Temporal Model for Early Drowsiness Detection", CVPR 2019.
