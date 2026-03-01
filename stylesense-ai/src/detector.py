import onnxruntime as ort
import numpy as np
from PIL import Image
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ONNX_PATH = BASE_DIR / "models" / "clothing_custom.onnx"

CATEGORIES = [
    "accessories", "dress", "jacket", "jeans", "pants", 
    "shirt", "shoes", "shorts", "skirt", "t-shirt"
]

class ClothingDetector:
    """Production-ready ONNX inference wrapper loaded once into memory."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        if not ONNX_PATH.exists():
            raise FileNotFoundError(f"ONNX model missing at {ONNX_PATH}. Train and export first.")
        
        # Optimize for best available execution provider (CoreML/CUDA/CPU)
        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.session = ort.InferenceSession(
            str(ONNX_PATH), 
            sess_options=options,
            providers=['CoreMLExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        self.input_name = self.session.get_inputs()[0].name
        print(f"🚀 ClothingDetector initialized successfully with providers: {self.session.get_providers()}")

    def _preprocess(self, image_path: str) -> np.ndarray:
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224), Image.Resampling.BILINEAR)
        img_data = np.array(image).astype("float32") / 255.0

        # Standard ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406]).astype("float32")
        std = np.array([0.229, 0.224, 0.225]).astype("float32")
        img_data = (img_data - mean) / std

        # Convert HWC to NCHW
        img_data = np.transpose(img_data, (2, 0, 1))
        img_data = np.expand_dims(img_data, axis=0)
        return img_data

    def predict(self, image_path: str) -> dict:
        """Runs the ONNX model returning predicted category and confidence."""
        try:
            input_tensor = self._preprocess(image_path)
            outputs = self.session.run(None, {self.input_name: input_tensor})[0]
            
            # Softmax
            exp_preds = np.exp(outputs[0] - np.max(outputs[0]))
            probs = exp_preds / exp_preds.sum()
            
            pred_idx = np.argmax(probs)
            confidence = float(probs[pred_idx])
            
            return {
                "prediction": CATEGORIES[pred_idx],
                "confidence": round(confidence, 4)
            }
        except Exception as e:
            print(f"❌ Inference error on {image_path}: {e}")
            return {"prediction": "unknown", "confidence": 0.0}

# Singleton instance convenience function
_detector = None

def get_prediction(image_path: str) -> dict:
    global _detector
    if _detector is None:
        _detector = ClothingDetector()
    return _detector.predict(image_path)

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        print(get_prediction(sys.argv[1]))
    else:
        print("Provide an image path to test: python src/detector.py path/to/img.jpg")
