# Model Information

## ✅ Current Active Model

The backend is now using the **best performing model** from your training runs.

### Model Details

- **Model Name**: drowsiness_detection-2
- **Architecture**: YOLOv8n Classification
- **Model Size**: 8.36 MB
- **Location**: `backend/weights/best.pt`
- **Source**: `ml_pipeline/models/drowsiness_detection-2/weights/best.pt`

### Training Results

#### drowsiness_detection-2 (ACTIVE MODEL)
- **Training Accuracy**: **99.75%** ⭐
- **Validation Loss**: 0.0115
- **Top-1 Accuracy**: 99.75%
- **Top-5 Accuracy**: 100%
- **Epochs Completed**: 1 out of 50
- **Training Time**: ~28 minutes (1,673 seconds)
- **Status**: Best model selected

#### Other Models (Kept for Reference)

**drowsiness_detection**
- Training Accuracy: 98.44%
- Validation Loss: 0.047
- Epochs: 1/50
- Location: `ml_pipeline/models/drowsiness_detection/`

**drowsiness_detection-3**
- Training Accuracy: 40.46% (Poor)
- Validation Loss: 0.987
- Epochs: 3/50
- Location: `ml_pipeline/models/drowsiness_detection-3/`

### Model Configuration

```yaml
Architecture: YOLOv8n-cls
Input Size: 224x224
Batch Size: 32
Learning Rate: 0.01
Optimizer: SGD
Device: CPU
Classes: 2 (Alert, Drowsy)
```

### Classes

The model predicts two classes:
1. **Alert** (Label 0) - Driver is awake and attentive
2. **Drowsy** (Label 1) - Driver shows signs of fatigue

### Performance Metrics

| Metric | Value |
|--------|-------|
| **Training Accuracy** | 99.75% |
| **Validation Loss** | 0.0115 |
| **Top-1 Accuracy** | 99.75% |
| **Top-5 Accuracy** | 100% |
| **Model Size** | 8.36 MB |

### Dataset Used for Training

- **Original Dataset**: Driver Drowsiness Dataset (DDD)
- **Note**: This model was trained on the old dataset
- **New Dataset Available**: UTA-RLDD (9,054 images)
- **Recommendation**: Retrain with UTA-RLDD for production use

### Backend Integration

The model is automatically loaded on backend startup:

```python
# Backend loads model from
backend/weights/best.pt

# Model manager handles inference
from app.models.model import model_manager
model = model_manager.get_model()
```

### API Endpoints Using This Model

- `POST /predict` - Upload image for drowsiness detection
- `GET /health` - Check if model is loaded

### Model Inference Pipeline

```
User uploads image
    ↓
decode_image() - Convert bytes to numpy array
    ↓
preprocess_for_yolo() - BGR to RGB conversion
    ↓
model.predict() - YOLO inference
    ↓
format_prediction() - Format results with severity
    ↓
Return: {label, confidence, status, severity, color}
```

### Next Steps

#### For Testing (Current Setup)
✅ Ready to use! Open http://localhost:3000

#### For Production (Recommended)
1. Train new model with UTA-RLDD dataset:
   ```bash
   cd ml_pipeline
   python train.py --model yolo --epochs 50
   ```

2. Copy trained model to backend:
   ```bash
   copy ml_pipeline\models\drowsiness_detection\weights\best.pt backend\weights\best.pt
   ```

3. Restart backend to load new model

### Training History

All training artifacts are preserved in `ml_pipeline/models/`:
- `drowsiness_detection/` - First training run (98.44%)
- `drowsiness_detection-2/` - **Best model** (99.75%) ⭐ ACTIVE
- `drowsiness_detection-3/` - Third run (40.46%)

Each folder contains:
- `weights/best.pt` - Best model weights
- `weights/last.pt` - Last epoch weights
- `results.csv` - Training metrics
- `args.yaml` - Training configuration
- `train_batch*.jpg` - Training visualizations

### Model Limitations

1. **Limited Training**: Only 1 epoch completed (target: 50)
2. **Old Dataset**: Trained on DDD, not UTA-RLDD
3. **CPU Inference**: Slower than GPU (suitable for demo)
4. **No Face Detection**: Expects face-centered images

### Improvements for Future

1. Complete full 50-epoch training with UTA-RLDD
2. Add face detection preprocessing
3. Implement GPU acceleration
4. Add eye region focus
5. Deploy with TensorRT/ONNX optimization

---

**Last Updated**: 2026-08-24  
**Model Active Since**: 2026-08-24  
**Backend Status**: ✅ Running with drowsiness_detection-2
