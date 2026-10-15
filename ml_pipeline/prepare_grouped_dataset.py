import hashlib
import shutil
from pathlib import Path

import config


SOURCE = config.DATA_DIR
OUTPUT = config.BASE_DIR / "data" / "uta_rldd_yolo"

SPLITS = ("train", "val", "test")
CLASSES = {
    "active": "Alert",
    "fatigue": "Drowsy",
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def main():
    if OUTPUT.exists():
        raise FileExistsError(
            f"{OUTPUT} already exists. Rename or remove that folder manually "
            "before running this script again."
        )

    # Check that the Kaggle dataset has all expected splits and classes.
    for split in SPLITS:
        for source_class in CLASSES:
            folder = SOURCE / split / source_class
            if not folder.is_dir():
                raise FileNotFoundError(f"Expected dataset folder: {folder}")

    # Do not copy byte-identical images with conflicting labels or into
    # multiple splits. The source labels cannot be inferred safely here.
    records = []
    hashes = {}
    for split in SPLITS:
        for source_class, output_class in CLASSES.items():
            source_folder = SOURCE / split / source_class
            for image in source_folder.iterdir():
                if not image.is_file() or image.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                digest = hashlib.sha256(image.read_bytes()).hexdigest()
                records.append((split, source_class, output_class, image, digest))
                hashes.setdefault(digest, []).append((split, source_class, image))

    skip_hashes = {
        digest for digest, copies in hashes.items()
        if len({source_class for _, source_class, _ in copies}) > 1
        or len({split for split, _, _ in copies}) > 1
    }
    if skip_hashes:
        print(
            f"Warning: excluding {sum(1 for r in records if r[4] in skip_hashes)} "
            "exact duplicates with conflicting labels or split leakage."
        )

    OUTPUT.mkdir(parents=True)

    for split in SPLITS:
        for source_class, output_class in CLASSES.items():
            source_folder = SOURCE / split / source_class
            output_folder = OUTPUT / split / output_class
            output_folder.mkdir(parents=True)

            images = [
                path for split_name, source_name, _, path, digest in records
                if split_name == split
                and source_name == source_class
                and digest not in skip_hashes
            ]

            if not images:
                raise ValueError(f"No images found in {source_folder}")

            for image in images:
                shutil.copy2(image, output_folder / image.name)

            print(f"{split}/{output_class}: copied {len(images)} images")

    print(f"\nDataset ready at: {OUTPUT}")


if __name__ == "__main__":
    main()
