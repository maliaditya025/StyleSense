import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PTH = BASE_DIR / "models" / "clothing_custom.pth"
ONNX_PATH = BASE_DIR / "models" / "clothing_custom.onnx"
NUM_CLASSES = 10

def export_to_onnx():
    if not MODEL_PTH.exists():
        print(f"❌ Source PyTorch model not found: {MODEL_PTH}")
        return

    print("🧠 Building MobileNetV2 architecture...")
    model = models.mobilenet_v2(weights=None)
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.last_channel, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, NUM_CLASSES)
    )

    print(f"📥 Loading weights from {MODEL_PTH}...")
    model.load_state_dict(torch.load(MODEL_PTH, map_location="cpu"))
    model.eval()

    print("📦 Exporting to ONNX format...")
    # Dummy input indicating (batch_size, channels, height, width)
    dummy_input = torch.randn(1, 3, 224, 224)

    torch.onnx.export(
        model, 
        dummy_input, 
        str(ONNX_PATH),
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "output": {0: "batch_size"}
        }
    )
    
    size_mb = os.path.getsize(ONNX_PATH) / (1024 * 1024)
    print(f"✅ Successfully exported to {ONNX_PATH} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    export_to_onnx()
