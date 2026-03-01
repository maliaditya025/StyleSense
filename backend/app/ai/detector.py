"""
CNN-based clothing category detector using MobileNetV2.

Three modes of operation (in priority order):
  1. CUSTOM ONNX MODEL: If clothing_custom.onnx exists, uses custom-trained model.
  2. IMAGENET ONNX MODEL: If clothing_classifier.onnx exists, uses ImageNet model
     with class mapping to clothing categories.
  3. HEURISTIC FALLBACK: Uses image analysis (aspect ratio, color, edge detection)
     when no ONNX model is available.

Deployment:
  - Local dev: Can use any mode (PyTorch for training, ONNX for inference)
  - Render: Uses ONNX Runtime (~20MB) for lightweight inference
  - onnxruntime replaces the heavy TensorFlow/PyTorch dependency

Supported categories:
  shirt, t-shirt, pants, jeans, shoes, jacket, dress, accessories, shorts, skirt
"""

import os
import numpy as np
from pathlib import Path

import cv2

# ═══════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════

IMG_SIZE = 224

CATEGORIES = [
    "shirt", "t-shirt", "pants", "jeans", "shoes",
    "jacket", "dress", "accessories", "shorts", "skirt",
]

VALID_CATEGORIES = set(CATEGORIES)

# ImageNet class → clothing category mapping (for pretrained model)
IMAGENET_MAP = {
    "jersey": "t-shirt", "T-shirt": "t-shirt", "tee_shirt": "t-shirt",
    "sweatshirt": "t-shirt",
    "jean": "jeans", "jeans": "jeans",
    "suit": "shirt", "Windsor_tie": "shirt", "bow_tie": "shirt",
    "lab_coat": "jacket", "trench_coat": "jacket", "fur_coat": "jacket",
    "military_uniform": "jacket", "cardigan": "jacket", "poncho": "jacket",
    "vestment": "jacket", "cloak": "jacket", "stole": "jacket",
    "kimono": "dress", "gown": "dress", "overskirt": "dress",
    "hoopskirt": "dress", "sarong": "dress",
    "miniskirt": "skirt",
    "running_shoe": "shoes", "Loafer": "shoes", "sandal": "shoes",
    "clog": "shoes", "cowboy_boot": "shoes", "boot": "shoes",
    "sock": "accessories", "sunglasses": "accessories",
    "sunglass": "accessories", "backpack": "accessories",
    "purse": "accessories", "wallet": "accessories",
    "knot": "accessories", "necklace": "accessories",
    "swimming_trunks": "shorts",
    "bikini": "dress", "brassiere": "accessories",
    "maillot": "t-shirt", "pajama": "pants",
    "abaya": "dress", "academic_gown": "dress",
}

# ═══════════════════════════════════════════════════════════════════════
# ONNX RUNTIME INFERENCE
# ═══════════════════════════════════════════════════════════════════════

# Lazy-loaded ONNX sessions
_onnx_custom = None
_onnx_imagenet = None
_onnx_available = None


def _check_onnx():
    """Check if onnxruntime is available."""
    global _onnx_available
    if _onnx_available is None:
        try:
            import onnxruntime
            _onnx_available = True
        except ImportError:
            _onnx_available = False
            print("⚠️  onnxruntime not installed — using heuristic-only detection")
    return _onnx_available


def _get_custom_onnx():
    """Load custom-trained ONNX model if available."""
    global _onnx_custom
    model_path = Path(__file__).parent / "clothing_custom.onnx"
    if model_path.exists() and _onnx_custom is None and _check_onnx():
        import onnxruntime as ort
        print(f"🧠 Loading custom ONNX model from {model_path}")
        _onnx_custom = ort.InferenceSession(str(model_path))
    return _onnx_custom


def _get_imagenet_onnx():
    """Load pretrained ImageNet ONNX model if available."""
    global _onnx_imagenet
    model_path = Path(__file__).parent / "clothing_classifier.onnx"
    if model_path.exists() and _onnx_imagenet is None and _check_onnx():
        import onnxruntime as ort
        print(f"🧠 Loading ImageNet ONNX model from {model_path}")
        _onnx_imagenet = ort.InferenceSession(str(model_path))
    return _onnx_imagenet


def _preprocess_image(img_path: str) -> np.ndarray:
    """Preprocess image for MobileNetV2 (ONNX)."""
    img = cv2.imread(img_path)
    if img is None:
        return None
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img.astype(np.float32) / 255.0

    # ImageNet normalization
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img = (img - mean) / std

    # CHW format, add batch dimension
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img


def _softmax(x):
    """Compute softmax probabilities."""
    e = np.exp(x - np.max(x))
    return e / e.sum()


def _predict_custom_onnx(img_path: str) -> dict:
    """Predict using custom-trained ONNX model."""
    session = _get_custom_onnx()
    if session is None:
        return None

    img = _preprocess_image(img_path)
    if img is None:
        return {"category": "t-shirt", "confidence": 0.0}

    # Load class mapping
    mapping_path = Path(__file__).parent / "class_mapping.txt"
    if mapping_path.exists():
        class_names = {}
        with open(mapping_path) as f:
            for line in f:
                idx, name = line.strip().split(":")
                class_names[int(idx)] = name
    else:
        class_names = {i: cat for i, cat in enumerate(sorted(CATEGORIES))}

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img})[0][0]
    probs = _softmax(outputs)

    idx = int(np.argmax(probs))
    category = class_names.get(idx, "t-shirt")
    confidence = float(probs[idx])

    return {
        "category": category,
        "confidence": round(confidence, 4),
        "method": "custom_onnx",
    }


def _predict_imagenet_onnx(img_path: str) -> dict:
    """Predict using pretrained ImageNet ONNX model with class mapping."""
    session = _get_imagenet_onnx()
    if session is None:
        return None

    img = _preprocess_image(img_path)
    if img is None:
        return {"category": "t-shirt", "confidence": 0.0}

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img})[0][0]
    probs = _softmax(outputs)

    # Map top ImageNet predictions to clothing categories
    # Load ImageNet class labels
    top_indices = np.argsort(probs)[::-1][:30]

    # We need ImageNet class names — use a built-in mapping
    imagenet_labels = _get_imagenet_labels()

    scores = {cat: 0.0 for cat in CATEGORIES}
    for idx in top_indices:
        class_name = imagenet_labels.get(idx, "")
        mapped = IMAGENET_MAP.get(class_name)
        if mapped:
            scores[mapped] += float(probs[idx])

    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]

    return {
        "category": best_cat,
        "confidence": round(best_score, 4),
        "method": "imagenet_onnx",
        "all_scores": {k: round(v, 4) for k, v in scores.items() if v > 0},
    }


# ImageNet label index → name mapping (subset relevant to clothing)
_imagenet_labels_cache = None


def _get_imagenet_labels() -> dict:
    """Get ImageNet class index to name mapping."""
    global _imagenet_labels_cache
    if _imagenet_labels_cache is not None:
        return _imagenet_labels_cache

    # Hardcoded mapping for clothing-relevant ImageNet classes
    _imagenet_labels_cache = {
        400: "academic_gown", 401: "accordion",
        610: "jersey", 611: "jigsaw_puzzle",
        834: "suit", 835: "mushroom",
        769: "running_shoe", 770: "safe",
        514: "clog", 515: "chain_link_fence",
        543: "cowboy_boot",
        630: "lab_coat", 631: "ladle",
        805: "sock", 806: "solar_dish",
        837: "sunglass", 838: "sunglasses",
        858: "sweatshirt", 859: "swimming_trunks",
        474: "cardigan", 475: "car_mirror",
        614: "kimono", 615: "knee_pad",
        676: "miniskirt", 677: "mink",
        508: "boot",
        690: "overskirt",
        689: "pajama",
        435: "bikini",
        449: "brassiere",
        457: "bow_tie",
        906: "Windsor_tie",
        414: "backpack",
        748: "purse",
        893: "wallet",
        469: "trench_coat",
        568: "fur_coat",
        671: "military_uniform",
        539: "cloak",
        823: "stole",
        765: "poncho",
        617: "gown",
        601: "hoopskirt",
        788: "sarong",
        655: "maillot",
        618: "abaya",
        440: "Loafer",
        774: "sandal",
    }
    return _imagenet_labels_cache


# ═══════════════════════════════════════════════════════════════════════
# HEURISTIC DETECTION (fallback when no model available)
# ═══════════════════════════════════════════════════════════════════════

def _heuristic_detect(img_path: str) -> dict:
    """
    Improved heuristic detection using aspect ratio, color, texture,
    and upper-body garment features (neckline, sleeves, symmetry).
    """
    img = cv2.imread(img_path)
    if img is None:
        return {"category": "t-shirt", "confidence": 0.0}

    h, w = img.shape[:2]
    ar = w / h

    # Color analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    avg_bright = float(np.mean(val))
    avg_sat = float(np.mean(sat))

    # Blue ratio (jeans indicator)
    blue_mask = (hue >= 90) & (hue <= 130) & (sat > 30)
    blue_ratio = float(np.sum(blue_mask)) / (h * w)

    # Texture
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    texture = float(np.std(gray))

    # Skin detection
    skin1 = cv2.inRange(hsv, np.array([0, 20, 70]), np.array([20, 255, 255]))
    skin2 = cv2.inRange(hsv, np.array([170, 20, 70]), np.array([180, 255, 255]))
    skin = skin1 | skin2
    third = h // 3
    skin_bot = float(np.sum(skin[2*third:, :] > 0)) / (third * w + 1)

    # Upper-body garment detection
    def _upper_body_score(gray, h, w):
        score = 0
        # Neckline edges in top 20%
        top_edges = cv2.Canny(gray[:h // 5, :], 50, 150)
        if float(np.sum(top_edges > 0)) / (h // 5 * w + 1) > 0.08:
            score += 2
        # Width variation (shoulders vs waist)
        bg_val = int(gray[0, 0])
        top_w = np.sum(np.abs(gray[h // 4, :].astype(int) - bg_val) > 30)
        bot_w = np.sum(np.abs(gray[3 * h // 4, :].astype(int) - bg_val) > 30)
        if top_w > 0 and bot_w > 0 and top_w / (bot_w + 1) > 0.9:
            score += 2
        # Symmetry
        left = gray[:, :w // 2]
        right = cv2.flip(gray[:, w // 2:], 1)
        min_w = min(left.shape[1], right.shape[1])
        if min_w > 10:
            sym = 1.0 - float(np.mean(np.abs(left[:, :min_w].astype(float) - right[:, :min_w].astype(float)))) / 255
            if sym > 0.85:
                score += 1
        # Center vertical edges (zipper/seam)
        sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        if float(np.mean(np.abs(sobel[:, w // 3: 2 * w // 3]))) > 15:
            score += 1
        # Top-half has more detail than bottom
        if float(np.std(gray[:h // 2, :])) > float(np.std(gray[h // 2:, :])) * 1.1:
            score += 1
        return score

    ub_score = _upper_body_score(gray, h, w)

    # Decision tree
    if blue_ratio > 0.15:
        return {"category": "jeans", "confidence": min(0.85, 0.5 + blue_ratio), "method": "heuristic"}
    if ar > 1.5:
        return {"category": "shoes", "confidence": 0.7, "method": "heuristic"}

    if ar < 0.6:
        if blue_ratio > 0.06:
            return {"category": "jeans", "confidence": 0.65, "method": "heuristic"}
        if ub_score >= 3:
            return {"category": "jacket" if avg_bright < 100 else "t-shirt", "confidence": 0.65, "method": "heuristic"}
        return {"category": "pants", "confidence": 0.7, "method": "heuristic"}

    if ar < 0.85:
        if blue_ratio > 0.06:
            return {"category": "jeans", "confidence": 0.6, "method": "heuristic"}
        if skin_bot > 0.35:
            return {"category": "shorts", "confidence": 0.6, "method": "heuristic"}
        if ub_score >= 3:
            if avg_bright < 100:
                return {"category": "jacket", "confidence": 0.65, "method": "heuristic"}
            return {"category": "shirt" if texture > 45 else "t-shirt", "confidence": 0.60, "method": "heuristic"}
        return {"category": "pants", "confidence": 0.65, "method": "heuristic"}

    if avg_bright < 100:
        return {"category": "jacket", "confidence": 0.55, "method": "heuristic"}
    if texture > 55:
        return {"category": "shirt", "confidence": 0.55, "method": "heuristic"}

    return {"category": "t-shirt", "confidence": 0.5, "method": "heuristic"}


# ═══════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════

def detect_clothing_category(image_path: str) -> str:
    """Detect clothing category. Returns category string."""
    result = detect_clothing_with_confidence(image_path)
    return result["category"]


def detect_clothing_with_confidence(image_path: str) -> dict:
    """
    Detect clothing category with confidence score.
    Returns: {"category": str, "confidence": float, "method": str}

    Priority:
      1. Custom ONNX model (trained on clothing data)
      2. ImageNet ONNX model (pretrained with class mapping)
      3. Heuristic fallback (aspect ratio + color + edge detection)
    """
    if not Path(image_path).exists():
        return {"category": "t-shirt", "confidence": 0.0, "method": "default"}

    # Priority 1: Custom trained ONNX model
    if _check_onnx():
        custom_result = _predict_custom_onnx(image_path)
        if custom_result and custom_result["confidence"] > 0.5:
            return custom_result

    # Priority 2: Pretrained ImageNet ONNX model
    if _check_onnx():
        imagenet_result = _predict_imagenet_onnx(image_path)
        if imagenet_result and imagenet_result["confidence"] > 0.3:
            # Combine with heuristic for better accuracy
            heuristic = _heuristic_detect(image_path)
            # If both agree, boost confidence
            if imagenet_result["category"] == heuristic["category"]:
                imagenet_result["confidence"] = min(0.95, imagenet_result["confidence"] + 0.15)
                imagenet_result["method"] = "onnx+heuristic"
            # If CNN says jacket but heuristic says pants (common confusion) - trust heuristic
            elif imagenet_result["category"] == "jacket" and heuristic["category"] in ("pants", "jeans", "shorts"):
                if heuristic["confidence"] > 0.5:
                    return heuristic
            return imagenet_result

    # Priority 3: Heuristic fallback
    return _heuristic_detect(image_path)
