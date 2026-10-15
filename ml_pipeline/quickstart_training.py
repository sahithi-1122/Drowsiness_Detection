"""
Quick-start interactive training script.

Automatically downloads the UTA-RLDD dataset if needed,
lets you configure training, runs it, and deploys the
best weights to the backend.

Usage:
    python quickstart_training.py
"""
import subprocess
import sys
from pathlib import Path

import config
from data_prep import load_image_paths_and_labels


def main():
    print("\n" + "=" * 70)
    print("Driver Drowsiness Detection — Quick Start Training (UTA-RLDD)")
    print("=" * 70 + "\n")

    # ── Step 1: Check / download dataset ─────────────────────────────────
    print("Step 1: Checking for dataset …")
    image_paths, labels = load_image_paths_and_labels()

    if not image_paths:
        print("\n📥 Dataset not found. Downloading from Kaggle …")
        print("   (one-time download; kagglehub will prompt for credentials)\n")
        try:
            from download_dataset import download_dataset
            download_dataset()
            image_paths, labels = load_image_paths_and_labels()
        except Exception as exc:
            print(f"\n❌ Download failed: {exc}")
            print("\nManual option:")
            print("  1. Visit https://www.kaggle.com/datasets/minhngt02/uta-rldd")
            print("  2. Download and extract so that ml_pipeline/data/ contains")
            print("     train/active, train/fatigue, test/active, test/fatigue")
            return

    if not image_paths:
        print("\n❌ Dataset downloaded but no images found. Check the folder structure.")
        return

    print(f"\n✓ Dataset ready: {len(image_paths):,} images\n")

    prepared_dataset = config.BASE_DIR / "data" / "uta_rldd_yolo"
    if not all((prepared_dataset / split).is_dir() for split in ("train", "val", "test")):
        print("Preparing the supplied train/val/test splits …")
        prep_script = Path(__file__).resolve().with_name("prepare_grouped_dataset.py")
        prep_result = subprocess.run(
            [sys.executable, str(prep_script)],
            cwd=str(config.BASE_DIR),
        )
        if prep_result.returncode != 0:
            print("\n❌ Dataset preparation failed.")
            return

    # ── Step 2: Training parameters ───────────────────────────────────────
    print("=" * 70)
    print("Step 2: Training Configuration")
    print("=" * 70)

    def _prompt(msg, default):
        raw = input(f"\n{msg} [default: {default}]: ").strip()
        return type(default)(raw) if raw else default

    epochs     = _prompt("Number of epochs", 50)
    batch_size = _prompt("Batch size (reduce to 16 if you run out of RAM)", 32)
    img_size   = _prompt("Image size", 224)

    # ── Step 3: Confirm & run ─────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Step 3: Summary")
    print("=" * 70)
    print(f"  Model      : YOLOv8n-cls (UTA-RLDD)")
    print(f"  Images     : {len(image_paths):,}")
    print(f"  Epochs     : {epochs}")
    print(f"  Batch size : {batch_size}")
    print(f"  Image size : {img_size}")

    go = input("\nStart training? (y/n) [y]: ").strip().lower() or "y"
    if go != "y":
        print("\nCancelled.")
        return

    print("\n🚀 Starting training …\n")
    result = subprocess.run(
        [
            sys.executable, "train.py",
            "--epochs",     str(epochs),
            "--batch-size", str(batch_size),
            "--img-size",   str(img_size),
        ]
    )

    if result.returncode != 0:
        print("\n❌ Training script exited with errors.")
        return

    # ── Step 4: Verify deployment ─────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Step 4: Verifying deployment")
    print("=" * 70)

    backend_weights = Path(__file__).resolve().parents[1] / "backend" / "weights" / "best.pt"
    if backend_weights.exists():
        print(f"\n✓ Model deployed to backend: {backend_weights}")
    else:
        print(f"\n⚠  Backend weights not found at {backend_weights}")
        yolo_best = config.MODELS_DIR / "yolo_best.pt"
        if yolo_best.exists():
            import shutil
            shutil.copy2(yolo_best, backend_weights)
            print(f"✓ Manually copied: {yolo_best} → {backend_weights}")

    print("\n" + "=" * 70)
    print("✅  All done!")
    print("=" * 70)
    print("\nStart the application:")
    print("  Terminal 1: cd ../backend  && uvicorn app.main:app --reload --port 8000")
    print("  Terminal 2: cd ../frontend && npm run dev")
    print("  Browser   : http://localhost:3000\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠  Interrupted.")
        sys.exit(1)
    except Exception as exc:
        print(f"\n\n❌ Error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
