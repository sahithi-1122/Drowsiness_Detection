"""
Training script — Driver Drowsiness Detection (UTA-RLDD)
Model: YOLOv8n-cls

Dataset: https://www.kaggle.com/datasets/minhngt02/uta-rldd
Classes: Alert (active) | Drowsy (fatigue)

Usage:
    python train.py                     # defaults: 50 epochs, img 224
    python train.py --epochs 80 --img-size 320
    python train.py --epochs 50 --batch-size 16   # if RAM is limited
"""
import argparse
import shutil
from pathlib import Path

import config
# from data_prep import (
#     load_image_paths_and_labels,
#     split_data,
#     prepare_yolo_dataset,
# )


def train_yolo_model(data_dir: Path, epochs: int, img_size: int, batch_size: int, workers: int = 4) -> object:
    """
    Fine-tune YOLOv8n-cls on the UTA-RLDD dataset.

    Args:
        data_dir   : Root of the YOLO-formatted dataset (contains train/val/test).
        epochs     : Max training epochs (early stopping is active).
        img_size   : Input image size (square).
        batch_size : Mini-batch size.
        workers    : DataLoader worker threads (set to 0 on Windows to avoid issues).

    Returns:
        Ultralytics training results object.
    """
    from ultralytics import YOLO

    print(f"\n{'='*55}")
    print("Training YOLOv8n-cls on UTA-RLDD")
    print(f"  data     : {data_dir}")
    print(f"  epochs   : {epochs}")
    print(f"  img_size : {img_size}")
    print(f"  batch    : {batch_size}")
    print(f"  workers  : {workers}")
    print(f"{'='*55}\n")

    model = YOLO("yolov8n-cls.pt")

    results = model.train(
        data=str(data_dir),
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        workers=workers,          # 0 on Windows avoids multiprocessing spawn issues
        name="drowsiness_detection",
        project=str(config.MODELS_DIR),
        patience=config.EARLY_STOPPING_PATIENCE,
        lr0=0.01,
        lrf=0.01,
        # Augmentation — helps a lot with face images
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.3,
        flipud=0.0,
        fliplr=0.5,
        degrees=10.0,
        translate=0.1,
        scale=0.3,
        erasing=0.3,
        auto_augment="randaugment",
        save=True,
        plots=True,
        verbose=True,
        exist_ok=False,
    )

    # Use the exact checkpoint from this training invocation.
    best_src = Path(model.trainer.best)
    best_dst = config.MODELS_DIR / "yolo_best.pt"

    if best_src.exists():
        shutil.copy2(best_src, best_dst)
        print(f"\n✓ Best weights copied to: {best_dst}")

        # Also deploy to backend automatically
        backend_dst = Path(__file__).resolve().parents[1] / "backend" / "weights" / "best.pt"
        if backend_dst.parent.exists():
            shutil.copy2(best_src, backend_dst)
            print(f"✓ Deployed to backend   : {backend_dst}")
    else:
        print(f"⚠  Best weights not found at {best_src}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Train YOLOv8n-cls drowsiness detector on UTA-RLDD"
    )
    parser.add_argument("--epochs",     type=int, default=50,
                        help="Max training epochs (default: 50)")
    parser.add_argument("--img-size",   type=int, default=224,
                        help="Input image size (default: 224)")
    parser.add_argument("--batch-size", type=int, default=32,
                        help="Batch size (default: 32; reduce to 16 if OOM)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("Driver Drowsiness Detection — Training (UTA-RLDD)")
    print(f"{'='*60}\n")
    # Use the prepared Kaggle train/val/test splits.
    yolo_data_dir = config.BASE_DIR / "data" / "uta_rldd_yolo"

    required_dirs = ("train", "val", "test")
    missing = [
        split for split in required_dirs
        if not (yolo_data_dir / split).is_dir()
    ]

    if missing:
        raise FileNotFoundError(
            f"Prepared dataset at {yolo_data_dir} is missing splits: {missing}. "
            "Run: python prepare_grouped_dataset.py"
        )

    print(f"Using dataset at: {yolo_data_dir}")
    # ── Train ────────────────────────────────────────────────────────────
    train_yolo_model(
        data_dir=yolo_data_dir,
        epochs=args.epochs,
        img_size=args.img_size,
        batch_size=args.batch_size,
        workers=0,   # 0 = safe default on Windows (avoids multiprocessing issues)
    )

    print(f"\n{'='*60}")
    print("Training complete!")
    print(f"{'='*60}\n")
    print("Next steps:")
    print("  1. Start backend : cd ../backend && uvicorn app.main:app --reload")
    print("  2. Start frontend: cd ../frontend && npm run dev")
    print("  3. Open browser  : http://localhost:3000\n")


if __name__ == "__main__":
    main()
