"""
Prepare YOLO dataset layout and start training.
Run from ml_pipeline/:  python _run_training.py
"""
import sys
from pathlib import Path

import config
from data_prep import load_image_paths_and_labels, split_data, prepare_yolo_dataset
from train import train_yolo_model

print("\n" + "="*60)
print("UTA-RLDD Training — YOLOv8n-cls")
print("="*60)

# ── 1. Load images ────────────────────────────────────────────
print("\n[1/3] Loading images …")
paths, labels = load_image_paths_and_labels()

if not paths:
    print("ERROR: no images found. Check DATA_DIR in config.py")
    sys.exit(1)

# ── 2. Split + prepare YOLO layout ───────────────────────────
print("\n[2/3] Splitting and preparing YOLO dataset …")
splits = split_data(paths, labels)
yolo_dir = prepare_yolo_dataset(splits)

# ── 3. Train ─────────────────────────────────────────────────
print("\n[3/3] Starting training …")
train_yolo_model(
    data_dir   = yolo_dir,
    epochs     = 50,
    img_size   = 224,
    batch_size = 16,   # safe for 16 GB RAM on CPU
    workers    = 0,    # required on Windows
)

print("\nTraining finished.")
