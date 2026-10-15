from pathlib import Path

from ultralytics import YOLO

"""Frame-wise threshold sweep on validation data only.

These metrics do not include the backend's temporal smoothing or alarm logic.
"""


HERE = Path(__file__).resolve().parent
DATASET = HERE / "data" / "uta_rldd_yolo"
WEIGHTS = HERE / "models" / "yolo_best.pt"
VAL_DIR = DATASET / "val"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def main():
    model = YOLO(str(WEIGHTS))

    drowsy_idx = next(
        index for index, name in model.names.items()
        if str(name).lower() == "drowsy"
    )

    samples = []
    for class_name, actual_drowsy in (("Alert", 0), ("Drowsy", 1)):
        class_dir = VAL_DIR / class_name
        for image in sorted(class_dir.iterdir()):
            if image.is_file() and image.suffix.lower() in IMAGE_EXTENSIONS:
                samples.append((image, actual_drowsy))

    if not samples:
        raise FileNotFoundError(f"No validation images found under {VAL_DIR}")

    scores = []
    for result in model.predict(
        source=[str(path) for path, _ in samples],
        stream=True,
        batch=32,
        verbose=False,
    ):
        scores.append(float(result.probs.data[drowsy_idx].item()))

    if len(scores) != len(samples):
        raise RuntimeError(
            f"Expected {len(samples)} predictions, got {len(scores)}"
        )

    actual = [label for _, label in samples]

    print("Validation-only frame metrics (not temporal/live-system metrics)")
    print("Threshold  Drowsy recall  Alert false-alarm rate  Accuracy")
    for threshold in (0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50):
        tp = fp = tn = fn = 0

        for true_label, drowsy_score in zip(actual, scores):
            predicted_drowsy = drowsy_score >= threshold

            if true_label == 1 and predicted_drowsy:
                tp += 1
            elif true_label == 1:
                fn += 1
            elif predicted_drowsy:
                fp += 1
            else:
                tn += 1

        recall = tp / (tp + fn) if tp + fn else 0
        false_alarm_rate = fp / (fp + tn) if fp + tn else 0
        accuracy = (tp + tn) / len(actual)

        print(
            f"{threshold:8.2f}  "
            f"{recall:13.1%}  "
            f"{false_alarm_rate:22.1%}  "
            f"{accuracy:8.1%}"
        )


if __name__ == "__main__":
    main()
