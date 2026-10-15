"""
Robust download script for UTA-RLDD dataset.

Uses kaggle CLI (not kagglehub) for reliable large-file downloads.
kaggle CLI handles resume, retries, and integrity checks better.

Usage:
    python download_uta_rldd.py
"""
import os
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path

DATASET_SLUG = "minhngt02/uta-rldd"
CACHE_DIR    = Path.home() / ".cache" / "kagglehub" / "datasets" / "minhngt02" / "uta-rldd" / "versions" / "2"
LOCAL_DIR    = Path(__file__).parent / "data"
ZIP_FILE     = LOCAL_DIR / "uta-rldd.zip"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}

def count_images(d: Path) -> int:
    return sum(1 for f in d.rglob("*") if f.suffix.lower() in IMG_EXTS) if d.exists() else 0

def check_already_extracted() -> bool:
    """Return True if dataset is already fully extracted."""
    for root in [CACHE_DIR, LOCAL_DIR]:
        train_active  = root / "train" / "active"
        train_fatigue = root / "train" / "fatigue"
        if train_active.exists() and train_fatigue.exists():
            n = count_images(train_active) + count_images(train_fatigue)
            if n > 5000:
                print(f"✓ Dataset already present at {root}")
                print(f"  Images found: {n:,}")
                return True
    return False

def install_kaggle_cli():
    print("Installing kaggle CLI …")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--quiet", "kaggle"])

def ensure_kaggle_credentials():
    """Check that kaggle.json exists."""
    cred_paths = [
        Path.home() / ".kaggle" / "kaggle.json",
        Path(os.environ.get("KAGGLE_CONFIG_DIR", "~/.kaggle")).expanduser() / "kaggle.json",
    ]
    for p in cred_paths:
        if p.exists():
            print(f"✓ Kaggle credentials found at {p}")
            return
    print("❌ kaggle.json not found!")
    print("   1. Go to https://www.kaggle.com/settings/account")
    print("   2. Click 'Create New API Token'")
    print("   3. Save the file to ~/.kaggle/kaggle.json")
    sys.exit(1)

def download_with_kaggle_cli():
    """Download using kaggle CLI — handles retries and large files cleanly."""
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remove any stale zip
    if ZIP_FILE.exists():
        ZIP_FILE.unlink()
        print("Removed stale zip.")

    print(f"\n📥 Downloading {DATASET_SLUG} via kaggle CLI …")
    print(f"   Destination: {LOCAL_DIR}\n")

    result = subprocess.run(
        [
            sys.executable, "-m", "kaggle",
            "datasets", "download",
            "-d", DATASET_SLUG,
            "-p", str(LOCAL_DIR),
            "--unzip",
        ],
        capture_output=False,   # stream output to terminal
    )

    if result.returncode != 0:
        print("\n❌ kaggle CLI download failed.")
        print("Trying kagglehub as fallback …")
        download_with_kagglehub()
    else:
        print("\n✓ Download complete via kaggle CLI.")

def download_with_kagglehub():
    """Fallback: use kagglehub with force_download to avoid cached corruption."""
    print("\n📥 Downloading via kagglehub (force=True) …")
    try:
        import kagglehub
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--quiet", "kagglehub"])
        import kagglehub

    path = kagglehub.dataset_download(DATASET_SLUG, force_download=True)
    print(f"✓ Downloaded to: {path}")
    return Path(path)

def locate_dataset_root() -> Path:
    """Find the root directory containing train/ and test/ sub-folders."""
    candidates = [
        CACHE_DIR,
        LOCAL_DIR,
        LOCAL_DIR / "uta-rldd",
    ]
    # Also search downloaded kagglehub cache
    kh_base = Path.home() / ".cache" / "kagglehub" / "datasets" / "minhngt02" / "uta-rldd"
    for v in sorted(kh_base.glob("versions/*"), reverse=True):
        candidates.append(v)

    for root in candidates:
        if (root / "train" / "active").exists():
            return root
    return None

def verify_and_report():
    root = locate_dataset_root()
    if root is None:
        print("\n❌ Could not find extracted dataset!")
        print("   Expected: train/active, train/fatigue, test/active, test/fatigue")
        return False

    train_active  = root / "train" / "active"
    train_fatigue = root / "train" / "fatigue"
    test_active   = root / "test"  / "active"
    test_fatigue  = root / "test"  / "fatigue"

    ta = count_images(train_active)
    tf = count_images(train_fatigue)
    xxa = count_images(test_active)
    xxf = count_images(test_fatigue)
    total = ta + tf + xxa + xxf

    print(f"\n✓ Dataset verified at: {root}")
    print(f"   train/active  (Alert) : {ta:>6,}")
    print(f"   train/fatigue (Drowsy): {tf:>6,}")
    if xxa or xxf:
        print(f"   test/active   (Alert) : {xxa:>6,}")
        print(f"   test/fatigue  (Drowsy): {xxf:>6,}")
    print(f"   Total                 : {total:>6,}")

    if total < 5000:
        print("\n⚠  Very few images found — dataset may be incomplete.")
        return False

    print("\n✓ Dataset looks complete!")
    print("   Run training with:")
    print("   cd ml_pipeline && python train.py --epochs 50\n")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("UTA-RLDD Dataset Downloader (Robust)")
    print("=" * 60)

    # 1. Already done?
    if check_already_extracted():
        verify_and_report()
        sys.exit(0)

    # 2. Ensure credentials
    ensure_kaggle_credentials()

    # 3. Try kaggle CLI (most reliable for large files)
    try:
        import kaggle  # noqa
    except ImportError:
        install_kaggle_cli()

    download_with_kaggle_cli()

    # 4. Verify
    ok = verify_and_report()
    sys.exit(0 if ok else 1)
