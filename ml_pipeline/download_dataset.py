"""
Download UTA-RLDD (UTA Real-Life Drowsiness Dataset) using kagglehub.

Dataset: https://www.kaggle.com/datasets/minhngt02/uta-rldd
Classes:
    active  → Alert  (label 0)
    fatigue → Drowsy (label 1)

Expected structure after download:
    <cache>/datasets/minhngt02/uta-rldd/versions/2/
    ├── train/
    │   ├── active/
    │   └── fatigue/
    └── test/
        ├── active/
        └── fatigue/
"""
import sys
import shutil
from pathlib import Path

import config


def _count_images(directory: Path) -> int:
    return sum(
        1 for f in directory.rglob("*")
        if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    ) if directory.exists() else 0


def download_dataset() -> Path:
    """
    Download UTA-RLDD dataset from Kaggle via kagglehub.

    Returns:
        Path to the dataset root directory.
    """
    print("\n" + "=" * 60)
    print("Downloading UTA-RLDD Dataset")
    print("Source : https://www.kaggle.com/datasets/minhngt02/uta-rldd")
    print("=" * 60 + "\n")

    try:
        import kagglehub
    except ImportError:
        print("❌ kagglehub not installed.")
        print("   Run: pip install kagglehub")
        sys.exit(1)

    print("📥 Downloading from Kaggle (first run requires authentication)...")
    dataset_path = Path(kagglehub.dataset_download("minhngt02/uta-rldd"))
    print(f"✓ Dataset downloaded to: {dataset_path}\n")

    # ── Validate structure ──────────────────────────────────────────────
    train_active  = dataset_path / "train" / "active"
    train_fatigue = dataset_path / "train" / "fatigue"
    test_active   = dataset_path / "test"  / "active"
    test_fatigue  = dataset_path / "test"  / "fatigue"

    if not (train_active.exists() and train_fatigue.exists()):
        print("⚠  Expected sub-folder structure not found.")
        print("   Looking deeper …")
        for p in sorted(dataset_path.rglob("active"))[:1]:
            print(f"   Found 'active' at: {p}")
        print(f"\n   Dataset root: {dataset_path}")
        print("   Please check the layout manually.")
        return dataset_path

    print("📊 Dataset statistics:")
    print(f"   Train / active  (Alert) : {_count_images(train_active):>6,} images")
    print(f"   Train / fatigue (Drowsy): {_count_images(train_fatigue):>6,} images")
    if test_active.exists():
        print(f"   Test  / active  (Alert) : {_count_images(test_active):>6,} images")
        print(f"   Test  / fatigue (Drowsy): {_count_images(test_fatigue):>6,} images")

    # ── Optionally mirror into ml_pipeline/data/ ────────────────────────
    local_data = Path(__file__).parent / "data"
    if local_data.resolve() != dataset_path.resolve():
        local_train = local_data / "train"
        local_test  = local_data / "test"

        if not local_train.exists():
            print(f"\n🔗 Linking dataset into {local_data} …")
            local_data.mkdir(exist_ok=True)
            try:
                (local_data / "train").symlink_to(
                    (dataset_path / "train").resolve(), target_is_directory=True
                )
                (local_data / "test").symlink_to(
                    (dataset_path / "test").resolve(), target_is_directory=True
                )
                print("✓ Symlinks created.")
            except OSError:
                print("⚠  Symlinks unavailable (Windows without admin). Copying …")
                shutil.copytree(dataset_path / "train", local_train)
                shutil.copytree(dataset_path / "test",  local_test)
                print("✓ Files copied.")
        else:
            print(f"\n✓ Local data directory already exists: {local_data}")

    print("\n" + "=" * 60)
    print("✓ Dataset ready!")
    print("=" * 60)
    print(f"\nRun training with:")
    print("  python train.py --epochs 50\n")

    return dataset_path


if __name__ == "__main__":
    try:
        download_dataset()
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        print("\nTroubleshooting:")
        print("  1. Install kagglehub : pip install kagglehub")
        print("  2. On first use kagglehub will prompt for Kaggle credentials.")
        print("     Get your API token from: https://www.kaggle.com/settings/account")
        raise
