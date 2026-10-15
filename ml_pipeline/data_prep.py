"""
Data preparation and loading utilities for UTA-RLDD dataset.

Dataset: https://www.kaggle.com/datasets/minhngt02/uta-rldd
Structure:
    <root>/
    ├── train/
    │   ├── active/      (Alert  – label 0)
    │   └── fatigue/     (Drowsy – label 1)
    └── test/
        ├── active/
        └── fatigue/
"""
import shutil
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

import config

_IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def load_image_paths_and_labels(
    data_dir: Path = None,
) -> Tuple[list, list]:
    """
    Load image paths and integer labels from the UTA-RLDD directory layout.

    Searches for the following folder pairs (in order of preference):
        active  / fatigue   (UTA-RLDD canonical)
        Alert   / Drowsy    (legacy copy)

    Args:
        data_dir: Root of the dataset.  Defaults to config.TRAIN_DATA_DIR.

    Returns:
        (image_paths, labels)  where label 0 = Alert, 1 = Drowsy.
    """
    if data_dir is None:
        data_dir = config.TRAIN_DATA_DIR

    data_dir = Path(data_dir)

    # Candidate folder pairs: (alert_folder, drowsy_folder)
    candidates = [
        (data_dir / "active",    data_dir / "fatigue"),
        (data_dir / "Alert",     data_dir / "Drowsy"),
        (data_dir / "Non Drowsy",data_dir / "Drowsy"),
        (data_dir / "Non_Drowsy",data_dir / "Drowsy"),
    ]

    for alert_dir, drowsy_dir in candidates:
        if alert_dir.exists() and drowsy_dir.exists():
            image_paths, labels = [], []
            for p in sorted(alert_dir.glob("*")):
                if p.suffix.lower() in _IMG_EXTS:
                    image_paths.append(str(p))
                    labels.append(0)
            for p in sorted(drowsy_dir.glob("*")):
                if p.suffix.lower() in _IMG_EXTS:
                    image_paths.append(str(p))
                    labels.append(1)

            if image_paths:
                print(f"✓ Loaded {len(image_paths)} images from {data_dir}")
                print(f"   Alert (active) : {labels.count(0):,}")
                print(f"   Drowsy (fatigue): {labels.count(1):,}")
                return image_paths, labels

    print(f"\n❌ No images found in {data_dir}")
    print("   Expected sub-folders: active/ and fatigue/")
    print("   Run: python download_dataset.py\n")
    return [], []


def split_data(
    image_paths: list,
    labels: list,
    train_split: float = config.TRAIN_SPLIT,
    val_split: float   = config.VAL_SPLIT,
    test_split: float  = config.TEST_SPLIT,
    random_state: int  = config.RANDOM_SEED,
) -> Dict[str, Tuple[list, list]]:
    """
    Stratified train / val / test split.

    Returns:
        {"train": (paths, labels), "val": ..., "test": ...}
    """
    assert abs(train_split + val_split + test_split - 1.0) < 1e-6, \
        "Splits must sum to 1.0"

    X_train, X_tmp, y_train, y_tmp = train_test_split(
        image_paths, labels,
        test_size=val_split + test_split,
        random_state=random_state,
        stratify=labels,
    )
    val_ratio = val_split / (val_split + test_split)
    X_val, X_test, y_val, y_test = train_test_split(
        X_tmp, y_tmp,
        test_size=1 - val_ratio,
        random_state=random_state,
        stratify=y_tmp,
    )

    print(f"\n✓ Data split:")
    print(f"   Train : {len(X_train):,}")
    print(f"   Val   : {len(X_val):,}")
    print(f"   Test  : {len(X_test):,}")

    return {
        "train": (X_train, y_train),
        "val":   (X_val,   y_val),
        "test":  (X_test,  y_test),
    }


def compute_class_weights(labels: list) -> Dict[int, float]:
    """Return balanced class weights keyed by integer label."""
    weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(labels),
        y=labels,
    )
    cw = {i: float(w) for i, w in enumerate(weights)}
    print(f"\n✓ Class weights: {cw}")
    return cw


def prepare_yolo_dataset(
    data_splits: Dict[str, Tuple[list, list]],
    output_dir: Path = None,
) -> Path:
    """
    Organise images into the YOLO classification folder layout:

        <output_dir>/
        ├── train/
        │   ├── Alert/
        │   └── Drowsy/
        ├── val/
        │   ├── Alert/
        │   └── Drowsy/
        └── test/
            ├── Alert/
            └── Drowsy/

    Images are **hard-linked** (or copied if cross-device) — no duplication
    of data on the same drive.

    Args:
        data_splits : Output of split_data().
        output_dir  : Destination root.  Defaults to DATA_DIR/yolo_dataset.

    Returns:
        Path to output_dir.
    """
    if output_dir is None:
        output_dir = config.DATA_DIR / "yolo_dataset"

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    class_names = config.CLASS_NAMES   # ["Alert", "Drowsy"]

    for split_name, (paths, labels) in data_splits.items():
        split_dir = output_dir / split_name
        split_dir.mkdir(exist_ok=True)

        # Pre-create class folders
        for cls in class_names:
            (split_dir / cls).mkdir(exist_ok=True)

        copied = 0
        for img_path, label in zip(paths, labels):
            src  = Path(img_path)
            dest = split_dir / class_names[label] / src.name
            if dest.exists():
                continue
            try:
                # Hard-link avoids duplicating data on same filesystem
                dest.hardlink_to(src)
            except (OSError, AttributeError):
                shutil.copy2(src, dest)
            copied += 1

        alert_n  = sum(1 for l in labels if l == 0)
        drowsy_n = sum(1 for l in labels if l == 1)
        print(f"✓ {split_name:5s}: {len(paths):,} images "
              f"(Alert={alert_n:,}, Drowsy={drowsy_n:,})")

    print(f"\n✓ YOLO dataset ready at: {output_dir}")
    return output_dir


# ─────────────────────────────────────────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing data preparation with UTA-RLDD dataset …")
    paths, labels = load_image_paths_and_labels()

    if not paths:
        print("Run: python download_dataset.py")
    else:
        splits = split_data(paths, labels)
        compute_class_weights(splits["train"][1])
        prepare_yolo_dataset(splits)
        print("\nAll done.")
