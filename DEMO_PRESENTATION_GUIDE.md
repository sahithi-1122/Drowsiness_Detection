# Driver Drowsiness Detection — Demo Guide

Use this guide to present the project from dataset preparation through the live web demo. Explain each file in your own words; do not read the code line by line.

## Before the presentation

- Keep the dataset and trained weights ready. Do not start a download or a full training run during the short demo.
- Start the backend in one PowerShell window:

  ```powershell
  cd backend
  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ```

- Start the frontend in a second PowerShell window:

  ```powershell
  cd frontend
  npm run dev
  ```

- Open the frontend URL printed by Next.js, allow camera access, and check that the backend reports as connected.

## Presentation order and speaking notes

### 1. Dataset

Show `ml_pipeline/download_uta_rldd.py` and `ml_pipeline/group_manifest.csv`.

Say: “We use the UTA-RLDD dataset, which contains driver images for Alert and Drowsy classification. The manifest records the image information used when preparing our dataset.”

If the dataset is already present, explain this step without running the downloader.

### 2. Dataset preparation

Show `ml_pipeline/prepare_grouped_dataset.py`, then point to `ml_pipeline/data/uta_rldd_yolo/`.

Say: “This step organizes the images into training, validation, and test sets in the format used by the classifier. Training data is used to teach the model, validation data helps us monitor it, and test data is used for a separate evaluation.”

### 3. Model training

Show `ml_pipeline/train.py`.

Say: “We trained a pretrained YOLOv8 classification model for Alert and Drowsy images. We used 224-pixel input images and a batch size of 16. Training was configured for up to 50 epochs and stopped after 25.”

### 4. Training results and evaluation

Show `ml_pipeline/models/drowsiness_detection/results.csv` and `ml_pipeline/evaluate.py`.

Say: “The training results record how the model performed during training. Its best validation accuracy was about 85.4%. The separate held-out test evaluation also measured about 85.4% top-1 accuracy.”

If asked about the operating threshold, show `ml_pipeline/tune_threshold.py`.

Say: “We compared thresholds on validation data. The selected 0.20 threshold detects more Drowsy examples, with some increase in Alert false alarms.”

### 5. Backend and model

Show `backend/app/main.py` and `backend/app/models/model.py`. Point out that the backend uses the trained weights in `backend/weights/best.pt`.

Say: “The backend starts the prediction service and loads the trained model once. It is ready to check camera images when the frontend sends them.”

Then show `backend/app/services/inference.py`.

Say: “This file sends an image through the model and returns an Alert or Drowsy prediction with confidence. The Drowsy probability threshold is 0.20.”

### 6. Additional image features and recent predictions

Show `backend/app/services/cv_features.py`.

Say: “The project calculates HOG, Sobel, morphology, and optical-flow values as additional image information. These values can be displayed, but they are not combined with the YOLO classifier’s decision.”

Then show `backend/app/services/temporal_analysis.py`.

Say: “The backend keeps up to 10 recent frame predictions to assess the recent pattern. Caution, Warning, and Danger are based on frame predictions; Danger means five consecutive Drowsy frames.”

Clarify: “The five-second browser beep is a separate timer. The danger level is based on frames, while the beep waits for Drowsy status to continue for five seconds.”

### 7. Backend prediction endpoint

Show `backend/app/routes/predict.py`.

Say: “This endpoint receives a camera image from the frontend, requests the prediction, and sends the result back.”

### 8. Frontend and live demonstration

Show `frontend/lib/api.js`, then `frontend/components/Camera.jsx`.

Say: “This is how the web page connects to the backend. The camera component captures frames and sends them for checking.”

Then show `frontend/app/page.jsx` and `frontend/components/DetectionResult.jsx`.

Say: “The page coordinates the live demo and displays the returned status and confidence. If Drowsy status continues for five seconds, the browser plays the audio alarm.”

Now demonstrate the running app: show the connected status, camera preview, current prediction, confidence, and alert display. Do not promise that the current system detects eye closure; eye detection is not driving the live prediction.

## Quick summary to close

“Our project takes webcam frames, classifies them as Alert or Drowsy, checks recent predictions, and displays the result in a web app. The trained model achieved about 85.4% top-1 accuracy on our held-out test set. The extra computer-vision values are displayed as supporting information, while the YOLO model makes the classification.”
