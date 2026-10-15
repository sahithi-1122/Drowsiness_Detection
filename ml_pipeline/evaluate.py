"""
Model evaluation script — UTA-RLDD dataset
Usage:
    python evaluate.py --model-path models/yolo_best.pt
"""
import argparse
from pathlib import Path

import config


def evaluate_yolo_model(model_path: str, dataset_root: Path) -> dict:
    """
    Run YOLO validation on the test split.

    Args:
        model_path   : Path to trained .pt weights.
        dataset_root : Root that contains train/ val/ test/ sub-folders.

    Returns:
        Dict with top-1 accuracy and full results object.
    """
    from ultralytics import YOLO

    print(f"Loading model : {model_path}")
    model = YOLO(model_path)

    # dataset_root must contain train/ val/ test/
    results = model.val(
        data=str(dataset_root),
        split="test",
        imgsz=config.YOLO_IMG_SIZE,
        verbose=True,
    )

    acc = results.results_dict.get("metrics/accuracy_top1", 0.0)
    return {"accuracy": acc, "results": results}


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate trained YOLOv8n-cls model on UTA-RLDD test set"
    )
    parser.add_argument(
        "--model-path", type=str,
        default=str(config.MODELS_DIR / "yolo_best.pt"),
        help="Path to trained YOLO weights (.pt)",
    )
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("Model Evaluation — UTA-RLDD")
    print(f"{'='*60}\n")

    yolo_dataset = config.BASE_DIR / "data" / "uta_rldd_yolo"
    if not yolo_dataset.exists():
        print("❌ YOLO dataset not prepared yet.")
        print("   Run: python train.py   (it prepares the dataset automatically)\n")
        return

    metrics = evaluate_yolo_model(
        model_path=args.model_path,
        dataset_root=yolo_dataset,
    )

    print(f"\n{'='*60}")
    print(f"Top-1 Accuracy : {metrics['accuracy']:.4f}  "
          f"({metrics['accuracy']*100:.1f}%)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
