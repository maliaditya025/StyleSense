"""
Export pretrained MobileNetV2 to ONNX format for lightweight deployment.

This exports the pretrained ImageNet model so the detector can use CNN
classification on Render via onnxruntime (~20MB) instead of PyTorch (~800MB).

Usage:
    python -m app.ai.export_onnx

Output:
    app/ai/clothing_classifier.onnx  (~14MB)
"""

import os
from pathlib import Path

import torch
import torchvision.models as models

MODEL_DIR = Path(__file__).parent
ONNX_PATH = MODEL_DIR / "clothing_classifier.onnx"
IMG_SIZE = 224


def export_pretrained():
    """Export pretrained MobileNetV2 (ImageNet 1000 classes) to ONNX."""
    print("🧠 Loading pretrained MobileNetV2...")
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    model.eval()

    # Dummy input for ONNX tracing
    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)

    print(f"📦 Exporting to ONNX: {ONNX_PATH}")
    torch.onnx.export(
        model,
        dummy,
        str(ONNX_PATH),
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
        opset_version=13,
    )

    size_mb = os.path.getsize(ONNX_PATH) / (1024 * 1024)
    print(f"✅ Exported: {ONNX_PATH} ({size_mb:.1f} MB)")


def export_custom(model_path: str, num_classes: int = 10):
    """Export a custom fine-tuned model to ONNX."""
    print(f"🧠 Loading custom model from {model_path}...")
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = torch.nn.Linear(model.last_channel, num_classes)

    state_dict = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)

    custom_onnx = MODEL_DIR / "clothing_custom.onnx"
    print(f"📦 Exporting custom model to: {custom_onnx}")
    torch.onnx.export(
        model,
        dummy,
        str(custom_onnx),
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
        opset_version=13,
    )

    size_mb = os.path.getsize(custom_onnx) / (1024 * 1024)
    print(f"✅ Custom model exported: {custom_onnx} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export MobileNetV2 to ONNX")
    parser.add_argument("--custom", type=str, default=None, help="Path to custom .pth model")
    parser.add_argument("--classes", type=int, default=10, help="Number of classes for custom model")
    args = parser.parse_args()

    if args.custom:
        export_custom(args.custom, args.classes)
    else:
        export_pretrained()
