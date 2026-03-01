# StyleSense AI — CNN Clothing Classifier

This repository contains the production-ready machine learning pipeline for StyleSense's clothing classifier. It is designed to train a robust, high-accuracy MobileNetV2 model on custom fashion datasets and export it to an optimized ONNX format for lightweight production deployment.

## Features
- **MobileNetV2 Architecture**: Pretrained on ImageNet, fine-tuned for 10 clothing categories.
- **Two-Phase Transfer Learning**: Freezes backbone to train the classifier head, then unfreezes the last 30% of layers for fine-tuning.
- **Advanced Data Augmentation**: `RandomResizedCrop`, `ColorJitter`, `RandomRotation`, and `RandomErasing` to prevent overfitting.
- **Class Balancing**: Uses `WeightedRandomSampler` to handle imbalanced datasets.
- **Hardware Acceleration**: Automatically detects and uses Apple Silicon MPS (Metal), CUDA, or CPU.
- **Production Export**: Exports to `.onnx` for lightweight deployment via `onnxruntime` (~20MB memory footprint instead of PyTorch's ~800MB).

## Directory Structure
\`\`\`text
stylesense-ai/
├── dataset/
│   ├── train/     # Put training images here, e.g., train/shirt/img1.jpg
│   ├── val/       # Put validation images here
│   └── test/      # Put testing images here (optional)
├── models/        # Trained .pth and exported .onnx models will be saved here
├── src/
│   ├── train.py         # Main training pipeline
│   ├── evaluate.py      # Generates classification report and confusion matrix
│   ├── export_onnx.py   # Exports .pth to .onnx
│   └── detector.py      # ONNX Runtime inference wrapper
├── requirements.txt
└── README.md
\`\`\`

## Getting Started

### 1. Install Dependencies
Ensure you are using Python 3.9+. It is recommended to use a virtual environment.
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Prepare the Dataset
Create the following structure inside the `dataset` folder with your images:
\`\`\`
dataset/
    train/
        shirt/
        pants/
        ... (10 categories)
    val/
        shirt/
        pants/
        ...
\`\`\`
*Target Categories:* `shirt`, `t-shirt`, `pants`, `jeans`, `shoes`, `jacket`, `dress`, `accessories`, `shorts`, `skirt`.

### 3. Train the Model
Run the two-phase training script. It features Early Stopping and will save the best model to `models/clothing_custom.pth`.
\`\`\`bash
python src/train.py
\`\`\`

### 4. Evaluate the Model (Optional)
Run the offline evaluation to generate a `classification_report` and a Confusion Matrix heatmap (`confusion_matrix.png`).
\`\`\`bash
python src/evaluate.py
\`\`\`

### 5. Export to ONNX for Production
Convert the heavy PyTorch model into a lightweight ONNX artifact (`models/clothing_custom.onnx`).
\`\`\`bash
python src/export_onnx.py
\`\`\`

### 6. Test Inference
Use the detector script to run a sample prediction using the efficient ONNX Runtime.
\`\`\`bash
python src/detector.py path/to/sample_image.jpg
\`\`\`

---
*Built for StyleSense AI Startup* 🚀
