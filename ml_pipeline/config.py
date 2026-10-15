"""
Configuration for model training
Dataset: UTA-RLDD (UTA Real-Life Drowsiness Dataset)
Source: https://www.kaggle.com/datasets/minhngt02/uta-rldd
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# UTA-RLDD dataset location (kagglehub cache)
KAGGLE_RLDD_PATH = (
    Path.home()
    / ".cache" / "kagglehub" / "datasets" / "minhngt02" / "uta-rldd" / "versions" / "2"
)
if KAGGLE_RLDD_PATH.exists():
    DATA_DIR = KAGGLE_RLDD_PATH

MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------
# UTA-RLDD dataset structure
#   <DATA_DIR>/
#   ├── train/
#   │   ├── active/      (Alert)
#   │   └── fatigue/     (Drowsy)
#   └── test/
#       ├── active/
#       └── fatigue/
# ------------------------------------------------------------
TRAIN_DATA_DIR = DATA_DIR / "train"
TEST_DATA_DIR  = DATA_DIR / "test"

ALERT_DIR   = TRAIN_DATA_DIR / "active"
DROWSY_DIR  = TRAIN_DATA_DIR / "fatigue"

IMG_SIZE      = (224, 224)  # For CNN-based models
YOLO_IMG_SIZE = 224         # Best balance of speed/accuracy for face crops

# Training configuration
BATCH_SIZE               = 32
EPOCHS                   = 50
LEARNING_RATE            = 0.001
TRAIN_SPLIT              = 0.70
VAL_SPLIT                = 0.15
TEST_SPLIT               = 0.15
RANDOM_SEED              = 42
EARLY_STOPPING_PATIENCE  = 10
REDUCE_LR_PATIENCE       = 5

# Model configuration
MODELS = {
    "yolo": {
        "base": "yolov8n-cls.pt",
        "img_size": YOLO_IMG_SIZE,
    }
}

# Data augmentation (used for non-YOLO models)
AUGMENTATION_CONFIG = {
    "rotation_range":    15,
    "width_shift_range":  0.1,
    "height_shift_range": 0.1,
    "brightness_range":  (0.8, 1.2),
    "horizontal_flip":   True,
    "zoom_range":         0.1,
    "fill_mode":         "nearest",
}

# Class names — UTA-RLDD binary classification
# active  → Alert  (label 0)
# fatigue → Drowsy (label 1)
CLASS_NAMES = ["Alert", "Drowsy"]
